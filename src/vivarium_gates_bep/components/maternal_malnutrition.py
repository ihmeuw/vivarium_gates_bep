import numpy as np
import pandas as pd
from risk_distributions import EnsembleDistribution
import scipy.optimize
from vivarium import Artifact
from vivarium.framework.randomness import get_hash
from vivarium_public_health.risks.data_transformations import pivot_categorical
from vivarium_public_health.risks.distributions import clip

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_beta_distribution, sample_gamma_distribution


class MaternalMalnutrition:

    @property
    def name(self):
        return f"risk.{project_globals.MATERNAL_MALNUTRITION_MODEL_NAME}"

    def setup(self, builder):
        self.exposure = self.load_exposure(builder)

        self.randomness = builder.randomness.get_stream(project_globals.MATERNAL_MALNUTRITION_MODEL_NAME)

        self.population_view = builder.population.get_view([project_globals.MOTHER_NUTRITION_STATUS_COLUMN])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[project_globals.MOTHER_NUTRITION_STATUS_COLUMN])

        builder.value.register_value_modifier('metrics', self.metrics)

    def on_initialize_simulants(self, pop_data):
        mother_nutrition_status = self.randomness.choice(
            pop_data.index,
            [project_globals.MOTHER_NUTRITION_MALNOURISHED, project_globals.MOTHER_NUTRITION_NORMAL],
            [self.exposure, 1 - self.exposure]
        )

        self.population_view.update(pd.DataFrame({
            project_globals.MOTHER_NUTRITION_STATUS_COLUMN: mother_nutrition_status
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
        return f"risk_effect.{project_globals.MATERNAL_MALNUTRITION_MODEL_NAME}"

    def setup(self, builder):
        self.relative_risk = self.load_relative_risk(builder)
        self.shifts = self.compute_shifts(builder, self.relative_risk)
        self.population_view = builder.population.get_view(
            ['sex', 'age', project_globals.MOTHER_NUTRITION_STATUS_COLUMN]
        )

        builder.value.register_value_modifier(
            f'{project_globals.LBWSG_MODEL_NAME}.exposure',
            self.adjust_birth_weight,
            requires_columns=[project_globals.MOTHER_NUTRITION_STATUS_COLUMN, 'sex']
        )
        builder.value.register_value_modifier(
            f'{project_globals.WASTING_MODEL_NAME}.exposure',
            self.adjust_wasting,
            requires_columns=[project_globals.MOTHER_NUTRITION_STATUS_COLUMN, 'sex', 'age']
        )
        builder.value.register_value_modifier(
            f'{project_globals.STUNTING_MODEL_NAME}.exposure',
            self.adjust_stunting,
            requires_columns=[project_globals.MOTHER_NUTRITION_STATUS_COLUMN, 'sex', 'age']
        )

    def adjust_birth_weight(self, index, exposure):
        pop = self.population_view.subview([project_globals.MOTHER_NUTRITION_STATUS_COLUMN, 'sex']).get(index)
        bw_shifts = self.shifts[project_globals.BIRTH_WEIGHT]
        for sex in ['Male', 'Female']:
            shift_up, shift_down = bw_shifts[sex]

            right_sex = pop.sex == sex
            mom_malnourished = (pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN]
                                == project_globals.MOTHER_NUTRITION_MALNOURISHED)

            exposure.loc[right_sex, project_globals.BIRTH_WEIGHT] += shift_up
            exposure.loc[right_sex & mom_malnourished, project_globals.BIRTH_WEIGHT] -= shift_down

        return exposure

    def adjust_wasting(self, index, exposure):
        return self.adjust_cgf(index, exposure, project_globals.WASTING_MODEL_NAME)

    def adjust_stunting(self, index, exposure):
        return self.adjust_cgf(index, exposure, project_globals.STUNTING_MODEL_NAME)

    def adjust_cgf(self, index, exposure, cgf_risk):
        pop = self.population_view.get(index)
        ages = pop.age.unique()
        shifts = self.shifts[cgf_risk]

        for age in ages:
            for (age_start, age_end, sex), (shift_up, shift_down) in shifts.items():
                if age_start <= age < age_end:
                    right_sex_and_age = (pop.sex == sex) & (pop.age == age)
                    mom_malnourished = (pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN]
                                        == project_globals.MOTHER_NUTRITION_MALNOURISHED)

                    exposure.loc[right_sex_and_age] += shift_up
                    exposure.loc[right_sex_and_age & mom_malnourished] -= shift_down

        return exposure

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
        wasting_shifts = compute_cgf_shifts(artifact_path, draw, location,
                                            project_globals.WASTING_MODEL_NAME, relative_risk)
        stunting_shifts = compute_cgf_shifts(artifact_path, draw, location,
                                             project_globals.STUNTING_MODEL_NAME, relative_risk)

        return {project_globals.BIRTH_WEIGHT: birth_weight_shifts,
                project_globals.WASTING_MODEL_NAME: wasting_shifts,
                project_globals.STUNTING_MODEL_NAME: stunting_shifts}


# TODO: A bunch of code here should be shared with the lbwsg component,
# but just trying to make things work for now.  Cleanup later.
def load_exposure(location, draw):
    key = f'{project_globals.MATERNAL_MALNUTRITION_MODEL_NAME}_exposure_draw_{draw}'
    seed = get_hash(key)
    mean = project_globals.MALNOURISHED_MOTHERS_PROPORTION_MEAN[location]
    variance = project_globals.MALNOURISHED_MOTHERS_PROPORTION_VARIANCE[location]
    exposure = sample_beta_distribution(seed, mean=mean, variance=variance, lower_bound=0, upper_bound=1)
    return exposure


def load_relative_risk(draw):
    key = f'{project_globals.MATERNAL_MALNUTRITION_MODEL_NAME}_relative_risk_draw_{draw}'
    seed = get_hash(key)
    return sample_gamma_distribution(seed, **project_globals.MALNOURISHED_MOTHERS_EFFECT_RR_PARAMETERS)


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


def compute_cgf_shifts(artifact_path, draw, location, cgf_risk, relative_risk):
    maternal_malnutrition_exposure = load_exposure(location, draw)
    mean_rr = relative_risk * maternal_malnutrition_exposure + 1 * (1 - maternal_malnutrition_exposure)
    paf = (mean_rr - 1) / mean_rr

    params, weights = get_cgf_exposure_parameters(artifact_path, draw, cgf_risk)
    sample_size = 100_000
    shifts = {}
    for idx, mean, sd in params.itertuples():
        if mean == 0:
            shifts[idx] = [0, 0]
            continue
        sample = sample_cgf_distribution(sample_size, mean, sd, weights, cgf_risk, idx)
        proportion_exposed = len(sample[sample < 8]) / len(sample)
        low_bmi_mask = np.random.choice([True, False], sample_size,
                                        p=[maternal_malnutrition_exposure, 1 - maternal_malnutrition_exposure])

        target_exposed = proportion_exposed * (1 - paf)

        def shift_up_objective(guess):
            exposure = sample + guess
            mean_exposed = len(exposure[exposure < 8]) / len(exposure)
            return (mean_exposed - target_exposed) ** 2

        shift_up = scipy.optimize.minimize(shift_up_objective, 1, method='Nelder-Mead', tol=1e-6).x[0]

        def shift_down_objective(guess):
            exposure = sample + shift_up
            exposure[low_bmi_mask] -= guess
            mean_exposed = len(exposure[exposure < 8]) / len(exposure)
            return (mean_exposed - proportion_exposed) ** 2

        shift_down = scipy.optimize.minimize(shift_down_objective, 1, method='Nelder-Mead', tol=1e-6).x[0]
        shifts[idx] = [shift_up, shift_down]

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
    data[project_globals.LBWSG_MISSING_CATEGORY.CAT] = project_globals.LBWSG_MISSING_CATEGORY.EXPOSURE
    return data


def get_birth_weight_categories(path):
    raw_category_dict = Artifact(path).load(f'risk_factor.low_birth_weight_and_short_gestation.categories')
    raw_category_dict[project_globals.LBWSG_MISSING_CATEGORY.CAT] = project_globals.LBWSG_MISSING_CATEGORY.NAME
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


def get_cgf_exposure_parameters(artifact_path, draw, risk):
    art = Artifact(artifact_path, [f'draw == {draw}'])
    mean = (art
            .load(f'alternative_risk_factor.{risk}.exposure')
            .rename(columns={f'draw_{draw}': 'mean'})
            .reset_index()
            .drop(columns=['location', 'parameter']))
    mean = (mean[(mean.age_start < 5) & (mean.year_start == 2017)]
            .drop(columns=['year_start', 'year_end'])
            .set_index(['age_start', 'age_end', 'sex']))
    sd = (art
          .load(f'alternative_risk_factor.{risk}.exposure_standard_deviation')
          .rename(columns={f'draw_{draw}': 'sd'})
          .reset_index()
          .drop(columns=['location']))
    sd = (sd[(sd.age_start < 5) & (sd.year_start == 2017)]
          .drop(columns=['year_start', 'year_end'])
          .set_index(['age_start', 'age_end', 'sex']))
    params = pd.concat([mean, sd], axis=1)
    w = (art
         .load(f'alternative_risk_factor.{risk}.exposure_distribution_weights')
         .reset_index()
         .drop(columns=['location']))

    w = (w[(w.age_start == 1) & (w.year_start == 2017)]
         .drop(columns=['age_start', 'age_end', 'year_start', 'year_end'])
         .set_index(['sex', 'parameter'])
         .unstack())
    w.columns = w.columns.droplevel()
    w.columns.name = None
    w = w.drop(columns='glnorm')
    w = w.loc['Female']
    return params, w


def sample_cgf_distribution(sample_size, mean, sd, weights, cgf_risk, group):
    seed = get_hash(f'{cgf_risk}_distribution_{group}')
    np.random.seed(seed)
    dist = EnsembleDistribution(weights=weights, mean=mean, sd=sd)
    np.random.seed(seed)
    q = np.random.random(sample_size)
    q = clip(q)
    return dist.ppf(q)
