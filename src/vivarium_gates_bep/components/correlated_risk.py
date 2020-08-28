"""
===================
Risk Exposure Model
===================

BirthweightCorrelatedRisk inherits from the base risk model and
adds a correlation to child growth failure (wasting and stunting)
based on birthweight. It works in concert with an extension to the
LBWSG code in this project

"""
import scipy
import numpy as np
import pandas as pd

from vivarium.framework.randomness import get_hash
from vivarium_public_health.risks import Risk
from vivarium_public_health.risks.data_transformations import get_exposure_post_processor

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_truncnorm


CORRELATION_VALUES = {
    # sample from truncated normal distribution created with the following parameters
    # mean, lower_bound, upper_bound, clip_lower, clip_upper
    'child_wasting': (0.308, 0.263, 0.351, 0.2, 0.4),
    'child_stunting': (0.394, 0.353, 0.433, 0.3, 0.5)
}


class BirthweightCorrelatedRisk(Risk):

    def __init__(self, risk: str):
        super().__init__(risk)

    def setup(self, builder):
        self.randomness = builder.randomness.get_stream(f'initial_{self.risk.name}_propensity')

        self.propensity_col = f'{self.risk.name}_propensity'
        birth_weight_propensity_col = project_globals.BIRTH_WEIGHT_PROPENSITY
        self.propensity = builder.value.register_value_producer(
            f'{self.risk.name}.propensity',
            source=lambda index: self.population_view.get(index)[self.propensity_col],
            requires_columns=[self.propensity_col])

        self.exposure = builder.value.register_value_producer(
            f'{self.risk.name}.exposure',
            source=self.get_current_exposure,
            requires_columns=['age', 'sex'],
            requires_values=[f'{self.risk.name}.propensity'],
            preferred_post_processor=get_exposure_post_processor(builder, self.risk)
        )

        self.population_view = builder.population.get_view([self.propensity_col, birth_weight_propensity_col])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.propensity_col],
                                                 requires_columns=[birth_weight_propensity_col],
                                                 requires_streams=[f'initial_{self.risk.name}_propensity'])

    def on_initialize_simulants(self, pop_data):
        """
        Abie supplied the method.

        Use BW percentile and specified correlation to find HAZ and WHZ percentiles

        1.) probit transform birth weight percentile to get birth weight normal

        2.) sample conditional bivariate normal for HAZ normal (conditional on BW normal, with specified correlation)

        3.) inverse probit transform HAZ normal to get HAZ percentile (aka "propensity")

        Repeat (2) and (3) for WHZ.
        """
        key = get_hash(f'{self.risk.name}_draw')
        corr_val = get_cgf_correlation_value(key, CORRELATION_VALUES[self.risk.name])

        tmp = self.population_view.subview([project_globals.BIRTH_WEIGHT_PROPENSITY]).get(pop_data.index)
        bw_propensity = correct_support_values(tmp)
        bw_probit = scipy.stats.norm.ppf(bw_propensity)[:,0]

        draw = self.randomness.get_draw(pop_data.index)
        target_probit = conditional_bivariate_normal(draw, bw_probit, corr_val)
        correlated_propensity = scipy.stats.norm.cdf(target_probit)
        self.population_view.update(pd.DataFrame({
                self.propensity_col: correlated_propensity,
            }, index=pop_data.index))


def conditional_bivariate_normal(draw, a, rho):
    # https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Bivariate_case_2
    # with mu1 = mu2 = 0 and sigma1 = sigma2 = 1
    norm = scipy.stats.norm(rho*a, np.sqrt((1-rho**2)))
    return norm.ppf(draw)


def get_cgf_correlation_value(seed, args):
    mean, lower_bound, upper_bound, clip_lower, clip_upper = args
    std = project_globals.confidence_interval_std(upper_bound, lower_bound)
    return sample_truncnorm(seed, mean, std, clip_lower, clip_upper)


def correct_support_values(bw_propensity):
    srt = bw_propensity.birth_weight_propensity.sort_values()
    lowest_value_idx = srt.index[0]
    next_lowest_value_idx = srt.index[1]
    highest_value_idx = srt.index[-1]
    next_highest_value_idx = srt.index[-2]
    if 0.0 == srt[lowest_value_idx]:
        bw_propensity.birth_weight_propensity[lowest_value_idx] = \
            bw_propensity.birth_weight_propensity[next_lowest_value_idx] / 2.0
    if 1.0 == srt[highest_value_idx]:
        bw_propensity.birth_weight_propensity[highest_value_idx] = \
            (1.0 - bw_propensity.birth_weight_propensity[next_highest_value_idx]) / 2.0
    return bw_propensity
