import pandas as pd
from vivarium.framework.randomness import get_hash

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sample_beta_distribution


class MaternalMalnutrition:

    @property
    def name(self):
        return "risk.maternal_malnutrition"

    def setup(self, builder):
        self.exposure = self.load_exposure(builder)

        self.randomness = builder.randomness.get_stream('maternal_malnutrition')

        self.column = 'mother_malnourished'
        self.population_view = builder.population.get_view([self.column])
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.column])

        builder.value.register_value_modifier('metrics', self.metrics)

    def on_initialize_simulants(self, pop_data):
        self.population_view.update(pd.DataFrame({
            self.column: self.randomness.choice(pop_data.index, [True, False], [self.exposure, 1 - self.exposure])
        }, index=pop_data.index))

    def load_exposure(self, builder):
        draw = builder.configuration.input_data.input_draw_number
        key = f'maternal_malnutrition_exposure_draw_{draw}'
        seed = get_hash(key)

        location = builder.configuration.input_data.location
        mean = project_globals.MALNOURISHED_MOTHERS_PROPORTION_MEAN[location]
        variance = project_globals.MALNOURISHED_MOTHERS_PROPORTION_VARIANCE[location]
        exposure = sample_beta_distribution(seed, mean=mean, variance=variance, lower_bound=0, upper_bound=1)
        return exposure

    def metrics(self, index, metrics):
        metrics[project_globals.MALNOURISHED_MOTHERS_PROPORTION_COLUMN] = self.exposure
        return metrics



