import pandas as pd
from vivarium.framework.randomness import get_hash

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_beta_distribution


class MaternalSupplementationCoverage:

    configuration_defaults = {
        project_globals.TREATMENT_MODEL_NAME: {
            'scenario': project_globals.SCENARIOS.BASELINE
        }
    }

    @property
    def name(self):
        return f'treatment.{project_globals.TREATMENT_MODEL_NAME}'

    def setup(self, builder):
        self.scenario = builder.configuration.maternal_supplementation.scenario
        if self.scenario not in project_globals.SCENARIOS:
            raise ValueError(f'Scenario must be one of {list(project_globals.SCENARIOS)}')
        self.baseline_coverage = self.load_coverage(builder, project_globals.SCENARIOS.BASELINE)
        self.scenario_coverage = self.load_coverage(builder, self.scenario)

        self.randomness = builder.randomness.get_stream(f'{project_globals.TREATMENT_MODEL_NAME}.propensity')
        columns = [project_globals.BASELINE_COLUMN, project_globals.SCENARIO_COLUMN]
        self.population_view = builder.population.get_view(columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns,
                                                 requires_columns=[project_globals.MOTHER_NUTRITION_STATUS_COLUMN])

    def on_initialize_simulants(self, pop_data):
        treatment = pd.DataFrame({
            project_globals.BASELINE_COLUMN: project_globals.TREATMENTS.NONE,
            project_globals.SCENARIO_COLUMN: project_globals.TREATMENTS.NONE
        }, index=pop_data.index)
        draw = self.randomness.get_draw(pop_data.index)
        baseline_treated = draw < self.baseline_coverage
        scenario_treated = draw < self.scenario_coverage

        treatment.loc[baseline_treated, project_globals.BASELINE_COLUMN] = project_globals.TREATMENTS.IFA

        if self.scenario in [project_globals.SCENARIOS.BASELINE, project_globals.SCENARIOS.IFA]:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.IFA
        elif self.scenario == project_globals.SCENARIOS.MMN:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.MMN
        elif self.scenario in [project_globals.SCENARIOS.BEP_CE, project_globals.SCENARIOS.BEP_HD]:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.BEP
        else:  # self.scenario == project_globals.SCENARIOS.BEP_TARGETED
            pop = self.population_view.subview([project_globals.MOTHER_NUTRITION_STATUS_COLUMN]).get(pop_data.index)
            mother_malnourished = (pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN]
                                   == project_globals.MOTHER_NUTRITION_MALNOURISHED)
            treatment.loc[scenario_treated & mother_malnourished] = project_globals.TREATMENTS.BEP
            treatment.loc[scenario_treated & ~mother_malnourished] = project_globals.TREATMENTS.MMN

        self.population_view.update(treatment)

    def load_coverage(self, builder, scenario):
        anc_proportion = self.load_anc_proportion(builder)
        if scenario == 'baseline':
            baseline_proportion_among_anc = self.load_ifa_proportion_among_anc(builder)
            return baseline_proportion_among_anc * anc_proportion
        else:
            scale_up_proportion_among_anc = 0.9
            return scale_up_proportion_among_anc * anc_proportion

    @staticmethod
    def load_anc_proportion(builder):
        anc = builder.data.load(project_globals.COVARIATE_ANC1_COVERAGE)
        anc = (anc[anc.year_start == 2017]
               .drop(columns=['year_start', 'year_end'])
               .set_index('parameter'))
        variance = project_globals.confidence_interval_variance(anc.loc['upper_value'], anc.loc['lower_value'])
        draw = builder.configuration.input_data.input_draw_number
        key = f'anc_coverage_proportion_draw_{draw}'
        seed = get_hash(key)
        return sample_beta_distribution(seed, anc.loc['mean_value'], variance, 0, 1)

    @staticmethod
    def load_ifa_proportion_among_anc(builder):
        draw = builder.configuration.input_data.input_draw_number
        key = f'maternal_ifa_proportion_among_anc_draw_{draw}'
        seed = get_hash(key)
        location = builder.configuration.input_data.location
        mean = project_globals.IFA_COVERAGE_AMONG_ANC_MEAN[location]
        variance = project_globals.IFA_COVERAGE_AMONG_ANC_VARIANCE[location]
        return sample_beta_distribution(seed, mean, variance, 0, 1)


class MaternalSupplementationEffect:

    def __init__(self, enable_adjust_cgf:str='True'):
        self._enable_adjust_cgf = enable_adjust_cgf=='True'

    @property
    def name(self):
        return f'treatment_effect.{project_globals.TREATMENT_MODEL_NAME}'

    def setup(self, builder):
        self.scenario = builder.configuration.maternal_supplementation.scenario
        self.treatment_effects = self.load_treatment_effects(builder)

        columns = [project_globals.BASELINE_COLUMN,
                   project_globals.SCENARIO_COLUMN,
                   project_globals.MOTHER_NUTRITION_STATUS_COLUMN]
        self.population_view = builder.population.get_view(columns)

        builder.value.register_value_modifier(f'{project_globals.LBWSG_MODEL_NAME}.exposure',
                                              self.adjust_lbwsg,
                                              requires_columns=columns)

        if self._enable_adjust_cgf:
            builder.value.register_value_modifier(f'{project_globals.STUNTING_MODEL_NAME}.exposure',
                                                  self.adjust_cgf,
                                                  requires_columns=columns)
            builder.value.register_value_modifier(f'{project_globals.WASTING_MODEL_NAME}.exposure',
                                                  self.adjust_cgf,
                                                  requires_columns=columns)

    def adjust_lbwsg(self, index, exposure):
        pop = self.population_view.get(index)
        baseline_covered = pop[project_globals.BASELINE_COLUMN] == project_globals.TREATMENTS.IFA
        exposure.loc[baseline_covered, project_globals.BIRTH_WEIGHT] -= self.treatment_effects[project_globals.TREATMENTS.IFA]

        ifa_covered = pop[project_globals.SCENARIO_COLUMN] == project_globals.TREATMENTS.IFA
        exposure.loc[ifa_covered, project_globals.BIRTH_WEIGHT] += self.treatment_effects[project_globals.TREATMENTS.IFA]

        mmn_covered = pop[project_globals.SCENARIO_COLUMN] == project_globals.TREATMENTS.MMN
        exposure.loc[mmn_covered, project_globals.BIRTH_WEIGHT] += self.treatment_effects[project_globals.TREATMENTS.MMN]

        bep_covered = pop[project_globals.SCENARIO_COLUMN] == self.scenario
        normal_effect = self.treatment_effects[project_globals.TREATMENTS.BEP][project_globals.BIRTH_WEIGHT]['normal']
        malnourished_effect = self.treatment_effects[project_globals.TREATMENTS.BEP][project_globals.BIRTH_WEIGHT]['malnourished']
        mother_malnourished = pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == project_globals.MOTHER_NUTRITION_MALNOURISHED
        exposure.loc[bep_covered & ~mother_malnourished, project_globals.BIRTH_WEIGHT] += normal_effect
        exposure.loc[bep_covered & mother_malnourished, project_globals.BIRTH_WEIGHT] += malnourished_effect
        return exposure

    def adjust_cgf(self, index, exposure):
        pop = self.population_view.get(index)
        bep_covered = pop[project_globals.SCENARIO_COLUMN] == self.scenario
        bep_effect = self.treatment_effects[project_globals.TREATMENTS.BEP]['cgf']
        exposure.loc[bep_covered] += bep_effect
        return exposure

    @staticmethod
    def load_treatment_effects(builder):
        scenario = builder.configuration.maternal_supplementation.scenario
        bep_effect_chooser = (project_globals.EFFECT_CURRENT_EVIDENCE
                           if '_ce_' in scenario else  project_globals.EFFECT_HOPES_AND_DREAMS)
        draw = builder.configuration.input_data.input_draw_number
        seed = get_hash(f'ifa_effect_size_draw_{draw}')
        ifa_effect = sample_beta_distribution(seed, **project_globals.IFA_BIRTH_WEIGHT_SHIFT_SIZE_PARAMETERS)
        seed = get_hash(f'mmn_effect_size_draw_{draw}')
        mmn_effect = sample_beta_distribution(seed, **project_globals.MMN_BIRTH_WEIGHT_SHIFT_SIZE_PARAMETERS)
        seed = get_hash(f'bep_effect_size_draw_{draw}')
        bep_normal_effect = sample_beta_distribution(
            seed, **project_globals.BEP_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_PARAMETERS[bep_effect_chooser]
        )
        bep_malnourished_effect = sample_beta_distribution(
            seed, **project_globals.BEP_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_PARAMETERS[bep_effect_chooser]
        )
        bep_cgf_effect = (sample_beta_distribution(
            seed, **project_globals.BEP_CGF_SHIFT_SIZE_PARAMETERS)
            if bep_effect_chooser == project_globals.EFFECT_HOPES_AND_DREAMS
            else project_globals.BEP_CE_CGF_SHIFT_SIZE)

        return {
            project_globals.TREATMENTS.NONE: 0,
            project_globals.TREATMENTS.IFA: ifa_effect,
            project_globals.TREATMENTS.MMN: mmn_effect,
            project_globals.TREATMENTS.BEP: {
                project_globals.BIRTH_WEIGHT: {
                    'normal': bep_normal_effect,
                    'malnourished': bep_malnourished_effect},
                'cgf': bep_cgf_effect,
            },
        }
