import numpy as np
import pandas as pd
import scipy.optimize
from vivarium import Artifact
from vivarium.framework.randomness import get_hash
from vivarium_public_health.risks.data_transformations import pivot_categorical

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_beta_distribution, sample_trianglular_distribution


MOTHER_MALNOURISHED_COLUMN = 'mother_malnourished'
MISSING_CATEGORY = 'cat212'


class MaternalMalnutrition:

    @property
    def name(self):
        return "risk.maternal_malnutrition"

    def setup(self, builder):
        self.exposure = self.load_exposure(builder)

        self.randomness = builder.randomness.get_stream('maternal_malnutrition')

        self.population_view = builder.population.get_view([MOTHER_MALNOURISHED_COLUMN])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[MOTHER_MALNOURISHED_COLUMN])

        builder.value.register_value_modifier('metrics', self.metrics)

    def on_initialize_simulants(self, pop_data):
        mother_malnourished = self.randomness.choice(pop_data.index,
                                                     [True, False],
                                                     [self.exposure, 1 - self.exposure])
        self.population_view.update(pd.DataFrame({
            MOTHER_MALNOURISHED_COLUMN: mother_malnourished
        }, index=pop_data.index))

    def metrics(self, index, metrics):
        metrics[project_globals.MALNOURISHED_MOTHERS_PROPORTION_COLUMN] = self.exposure
        return metrics

    @staticmethod
    def load_exposure(builder):
        location = builder.configuration.input_data.location
        draw = builder.configuration.input_data.input_draw_number
        return load_exposure(location, draw)


class MaternalMalnutritionRiskEffect:

    @property
    def name(self):
        return "risk_effect.maternal_malnutrition"

    def setup(self, builder):
        self.relative_risk = self.load_relative_risk(builder)
        self.shifts = self.compute_shifts(builder, self.relative_risk)
        self.population_view = builder.population.get_view([MOTHER_MALNOURISHED_COLUMN, 'sex'])

        builder.value.register_value_modifier('low_birth_weight_and_short_gestation.exposure',
                                              self.adjust_birth_weight,
                                              requires_columns=[MOTHER_MALNOURISHED_COLUMN, 'sex'])

    @staticmethod
    def load_relative_risk(builder):
        draw = builder.configuration.input_data.input_draw_number
        return load_relative_risk(draw)

    @staticmethod
    def compute_shifts(builder, relative_risk):
        artifact_path = builder.configuration.input_data.artifact_path
        draw = builder.configuration.input_data.input_draw_number
        location = builder.configuration.input_data.location
        birth_weight_shifts = compute_birth_weight_shift(artifact_path, draw, location, relative_risk)
        return {'birth_weight': birth_weight_shifts}

    def adjust_birth_weight(self, index, exposure):
        pop = self.population_view.get(index)
        bw_shifts = self.shifts['birth_weight']
        for sex in ['Male', 'Female']:
            shift_up, shift_down = bw_shifts[sex]
            exposure.loc[pop.sex == sex, 'birth_weight'] += shift_up
            exposure.loc[(pop.sex == sex) & pop[MOTHER_MALNOURISHED_COLUMN], 'birth_weight'] -= shift_down
        return exposure


# TODO: A bunch of code here should be shared with the lbwsg component,
# but just trying to make things work for now.  Cleanup later.

def load_exposure(location, draw):
    key = f'maternal_malnutrition_exposure_draw_{draw}'
    seed = get_hash(key)
    mean = project_globals.MALNOURISHED_MOTHERS_PROPORTION_MEAN[location]
    variance = project_globals.MALNOURISHED_MOTHERS_PROPORTION_VARIANCE[location]
    exposure = sample_beta_distribution(seed, mean=mean, variance=variance, lower_bound=0, upper_bound=1)
    return exposure


def load_relative_risk(draw):
    key = f'maternal_malnutrition_relative_risk_draw_{draw}'
    seed = get_hash(key)
    return sample_trianglular_distribution(seed, **project_globals.MALNOURISHED_MOTHERS_EFFECT_RR_PARAMETERS)


def compute_birth_weight_shift(artifact_path, draw, location, relative_risk):
    maternal_malnutrition_exposure = load_exposure(location, draw)
    mean_rr = relative_risk*maternal_malnutrition_exposure + 1*(1 - maternal_malnutrition_exposure)
    paf = (mean_rr - 1)/mean_rr

    lbwsg_exposure = read_lbwsg_data_by_draw(artifact_path, draw)
    birth_weight_categories = get_birth_weight_categories(artifact_path)

    sample_size = 100_000
    shifts = {}
    for sex in ['Male', 'Female']:
        sample = sample_lbwsg_distribution(sample_size, sex, lbwsg_exposure, birth_weight_categories)
        proportion_underweight = len(sample[sample.birth_weight < 2500])/len(sample)
        low_bmi_mask = np.random.choice([True, False], sample_size,
                                        p=[maternal_malnutrition_exposure, 1-maternal_malnutrition_exposure])

        target_underweight = proportion_underweight * (1 - paf)

        def shift_up_objective(guess):
            bw = sample.birth_weight + guess
            mean_bw = len(bw[bw < 2500])/len(bw)
            return (mean_bw - target_underweight)**2

        shift_up = scipy.optimize.minimize(shift_up_objective, 100, method='Nelder-Mead', tol=1e-6).x[0]

        def shift_down_objective(guess):
            bw = sample.birth_weight + shift_up
            bw[low_bmi_mask] -= guess
            mean_bw = len(bw[bw < 2500]) / len(bw)
            return (mean_bw - proportion_underweight) ** 2

        shift_down = scipy.optimize.minimize(shift_down_objective, 100, method='Nelder-Mead', tol=1e-6).x[0]
        shifts[sex] = [shift_up, shift_down]

    return shifts


def read_lbwsg_data_by_draw(artifact_path, draw):
    key = 'risk_factor/low_birth_weight_and_short_gestation/exposure'
    with pd.HDFStore(artifact_path, mode='r') as store:
        index = store.get(f'{key}/index')
        draw = store.get(f'{key}/draw_{draw}')
    draw = draw.rename("value")
    data = pd.concat([index, draw], axis=1)
    data = data.drop(columns='location')
    data = pivot_categorical(data)
    data = (data[(data.age_start == 0) & (data.year_start == 2017)]
            .drop(columns=['age_start', 'age_end', 'year_start', 'year_end'])
            .set_index('sex'))
    data[MISSING_CATEGORY] = 0.
    return data


def get_birth_weight_categories(path):
    raw_category_dict = Artifact(path).load(f'risk_factor.low_birth_weight_and_short_gestation.categories')
    raw_category_dict[MISSING_CATEGORY] = 'Birth prevalence - [37, 38) wks, [1000, 1500) g'
    category_dict = {'category': [],
                     'birth_weight_start': [],
                     'birth_weight_end': []}
    for key, value in raw_category_dict.items():
        birth_weight = value.split(' wks, ')[1]
        birth_weight_start, birth_weight_end = [
            int(item) for item in birth_weight.lstrip('[').rstrip(') g').split(', ')
        ]
        category_dict['category'].append(key)
        category_dict['birth_weight_start'].append(birth_weight_start)
        category_dict['birth_weight_end'].append(birth_weight_end)
    return pd.DataFrame(category_dict).set_index('category')


def sample_lbwsg_distribution(sample_size, sex, exposure, categories):
    seed = get_hash(f'birth_weight_distribution_{sex}')
    np.random.seed(seed)
    data = exposure.loc[sex, categories.index]
    choices = np.random.choice(data.index.values, sample_size, p=data.values)
    intervals = categories.loc[choices]
    birth_weights = np.random.uniform(intervals.birth_weight_start, intervals.birth_weight_end, sample_size)
    return pd.DataFrame({'birth_weight': birth_weights})
