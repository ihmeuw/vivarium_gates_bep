import pandas as pd
from vivarium_public_health import utilities

from vivarium_gates_bep import globals as project_globals


class NewbornPopulation:
    """Component for producing and aging simulants based on demographic data."""

    @property
    def name(self):
        return "base_population"

    def setup(self, builder):
        self.config = builder.configuration.population
        self.location = builder.configuration.input_data.location
        self.sex_probability = self.load_sex_probability(builder)

        self.randomness = builder.randomness.get_stream('population_sex')

        columns = ['index', 'age', 'sex', 'alive', 'location', 'entrance_time', 'exit_time']
        self.population_view = builder.population.get_view(columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns)
        self.register_simulants = builder.randomness.register_simulants

        # Need to age people after everything else since age is used for all the data.
        builder.event.register_listener('time_step__cleanup', self.on_time_step_cleanup)

    def on_initialize_simulants(self, pop_data):
        pop = pd.DataFrame({
            'index': pop_data.index.values
        }, index=pop_data.index)
        self.register_simulants(pop)
        sexes = self.sex_probability.index.to_list()
        pop['age'] = 0.
        pop['sex'] = self.randomness.choice(pop_data.index, sexes, self.sex_probability[sexes].values)
        pop['alive'] = 'alive'
        pop['location'] = self.location
        pop['entrance_time'] = pop_data.creation_time
        pop['exit_time'] = pd.NaT
        self.population_view.update(pop)

    def on_time_step_cleanup(self, event):
        """Ages simulants each time step."""
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['age'] += utilities.to_years(event.step_size)
        self.population_view.update(population)

    @staticmethod
    def load_sex_probability(builder):
        year_start = builder.configuration.time.start.year
        # Fixme: replace with live births
        pop_data = builder.data.load(project_globals.POPULATION_STRUCTURE)
        if year_start not in pop_data.year_start:
            year_start = pop_data.year_start.max()
        pop_data = pop_data.loc[(pop_data.year_start == year_start) & (pop_data.age_start == 0)]
        pop_data = pop_data.set_index('sex').value
        return pop_data / pop_data.sum()

    def __repr__(self):
        return "BasePopulation()"
