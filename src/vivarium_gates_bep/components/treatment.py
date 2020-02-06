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
        self.treatment_coverage = self.treatment_coverage(builder)

        self.randomness = builder.randomness.get_stream('maternal_supplementation.propensity')
        self.column = 'maternal_supplementation_type'
        self.population_view = builder.population.get_view([self.column])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.column],
                                                 requires_columns=['mother_malnourished'])

    def on_initialize_simulants(self, pop_data):
        treatment = pd.Series('none', index=pop_data.index, name=self.column)
        draw = self.randomness.get_draw(pop_data.index)
        treated = draw < self.treatment_coverage

        if self.scenario in [project_globals.SCENARIOS.BASELINE, project_globals.SCENARIOS.IFA]:
            treatment.loc[treated] = project_globals.TREATMENTS.IFA
        elif self.scenario == project_globals.SCENARIOS.MMN:
            treatment.loc[treated] = project_globals.TREATMENTS.MMN
        elif self.scenario == project_globals.SCENARIOS.BEP:
            treatment.loc[treated] = project_globals.TREATMENTS.BEP
        else:  # self.scenario == project_globals.SCENARIOS.BEP_TARGETED
            pop = pop_data.subview(['mother_malnourished']).get(pop_data.index)
            treatment.loc[treated & pop.mother_malnourished] = project_globals.TREATMENTS.BEP
            treatment.loc[treated & ~pop.mother_malnourished] = project_globals.TREATMENTS.MMN

        self.population_view.update(treatment)

    def load_scenario_parameters(self, builder):
        scenario = builder.configuration.maternal_supplementation.scenario
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
        import pdb; pdb.set_trace()

    @staticmethod
    def load_ifa_proportion_among_anc(builder):
        draw = builder.configuration.input_data.input_draw_number
        key = f'maternal_ifa_proportion_among_anc_draw_{draw}'
        seed = get_hash(key)
        return sample_beta_distribution(seed,
                                        mean=project_globals.IFA_COVERAGE_AMONG_ANC_MEAN,
                                        variance=project_globals.IFA_COVERAGE_AMONG_ANC_VARIANCE,
                                        lower_bound=0, upper_bound=1)


