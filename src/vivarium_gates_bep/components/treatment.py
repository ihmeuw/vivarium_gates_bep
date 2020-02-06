import pandas as pd
from vivarium.framework.randomness import get_hash

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_beta_distribution


class MaternalSupplementationCoverage:

    configuration_defaults = {
        'maternal_supplementation': {
            'scenario': project_globals.SCENARIOS.BASELINE
        }
    }

    @property
    def name(self):
        return 'treatment.maternal_supplementation'

    def setup(self, builder):
        self.scenario = builder.configuration.maternal_supplementation.scenario
        if self.scenario not in project_globals.SCENARIOS:
            raise ValueError(f'Scenario must be one of {list(project_globals.SCENARIOS)}')
        self.baseline_coverage = self.load_coverage(builder, project_globals.SCENARIOS.BASELINE)
        self.scenario_coverage = self.load_coverage(builder, self.scenario)

        self.randomness = builder.randomness.get_stream('maternal_supplementation.propensity')

        self.baseline_column = 'baseline_maternal_supplementation_type'
        self.scenario_column = 'scenario_maternal_supplementation_type'
        self.population_view = builder.population.get_view([self.baseline_column, self.scenario_column])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.baseline_column, self.scenario_column],
                                                 requires_columns=['mother_malnourished'])

    def on_initialize_simulants(self, pop_data):
        treatment = pd.DataFrame({
            self.baseline_column: project_globals.TREATMENTS.NONE,
            self.scenario_column: project_globals.TREATMENTS.NONE
        }, index=pop_data.index)
        draw = self.randomness.get_draw(pop_data.index)
        baseline_treated = draw < self.baseline_coverage
        scenario_treated = draw < self.scenario_coverage

        treatment.loc[baseline_treated, self.baseline_column] = project_globals.TREATMENTS.IFA

        if self.scenario in [project_globals.SCENARIOS.BASELINE, project_globals.SCENARIOS.IFA]:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.IFA
        elif self.scenario == project_globals.SCENARIOS.MMN:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.MMN
        elif self.scenario == project_globals.SCENARIOS.BEP:
            treatment.loc[scenario_treated] = project_globals.TREATMENTS.BEP
        else:  # self.scenario == project_globals.SCENARIOS.BEP_TARGETED
            pop = pop_data.subview(['mother_malnourished']).get(pop_data.index)
            treatment.loc[scenario_treated & pop.mother_malnourished] = project_globals.TREATMENTS.BEP
            treatment.loc[scenario_treated & ~pop.mother_malnourished] = project_globals.TREATMENTS.MMN

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


