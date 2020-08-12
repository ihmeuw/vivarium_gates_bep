"""
===================
Risk Exposure Model
===================

This module contains tools for modeling categorical and continuous risk
exposure.

"""
import scipy
import numpy as np
import pandas as pd

from vivarium_public_health.risks import Risk
from vivarium_public_health.risks.data_transformations import get_exposure_post_processor

from vivarium_gates_bep import globals as project_globals


CORR_WLZ = 0.308    # (0.263-0.351) we truncate at 0.2 and 0.4?
CORR_LAZ = 0.394    # (0.353 - 0.433) we can truncate at 0.3 to 0.5.


class CorrelatedRisk(Risk):

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
        bw_propensity = self.population_view.subview([project_globals.BIRTH_WEIGHT_PROPENSITY]).get(pop_data.index)
        bw_probit = scipy.stats.norm.ppf(bw_propensity)
        target_probit = conditional_bivariate_normal(bw_probit, CORR_WLZ)
        correlated_propensity = scipy.stats.norm.cdf(target_probit)[:, 0]
        #self.population_view.update(self.randomness.get_draw(pop_data.index))
        self.population_view.update(pd.DataFrame({
            self.propensity_col: correlated_propensity,
        }, index=pop_data.index))


def conditional_bivariate_normal(a, rho):
    # https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Bivariate_case_2
    # with mu1 = mu2 = 0 and sigma1 = sigma2 = 1
    return np.random.normal(rho*a, np.sqrt((1-rho**2)))
    # scipy.stats.norm use draw tied to our randomness system
