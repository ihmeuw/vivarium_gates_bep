import itertools

import pandas as pd

from vivarium_public_health.metrics import DiseaseObserver, MortalityObserver, DisabilityObserver
from vivarium_public_health.metrics.utilities import (
    get_output_template, QueryString, get_group_counts, to_years, get_years_lived_with_disability,
    get_person_time, get_deaths, get_years_of_life_lost
)

from vivarium_gates_bep import globals as project_globals


class BEPGatesMortalityObserver(MortalityObserver):

    def __init__(self):
        super().__init__()

    def setup(self, builder):
        super().setup(builder)
        # TODO confirm pipeline name
        self.malnourishment = builder.value.get_value(f'maternal_malnourishment.exposure')
        self.treatment_group = builder.value.get_value('treatment.exposure')

    def metrics(self, index, metrics):
        pop = self.population_view.get(index)
        pop.loc[pop.exit_time.isnull(), 'exit_time'] = self.clock()

        # TODO uncomment this once the pipelines have been created
        # pop_malnourishment_category = self.malnourishment(index)
        # pop_treatment_group = self.treatment_group(index)

        measure_getters = (
            (get_person_time, ()),
            (get_deaths, (project_globals.CAUSES_OF_DEATH,)),
            (get_years_of_life_lost, (self.life_expectancy, project_globals.CAUSES_OF_DEATH)),
        )

        groups = itertools.product(project_globals.MALNOURISHMENT_CATEGORIES, project_globals.AGE_GROUPS,
                                   project_globals.TREATMENT_GROUPS)
        for malnourishment_category, age_group, treatment_group in groups:
            malnourishment_state = project_globals.MALNOURISHMENT_MAP[malnourishment_category]
            # TODO uncomment this once the pipelines have been created
            # pop_in_group = pop.loc[
            #     pop_malnourishment_category == malnourishment_category
            #     & pop_treatment_group == treatment_group
            # ]
            # base_args = (pop_in_group, self.config.to_dict(), self.start_time, self.clock(), self.age_bins)
            base_args = (pop, self.config.to_dict(), self.start_time, self.clock(), self.age_bins)

            for measure_getter, extra_args in measure_getters:
                measure_data = measure_getter(*base_args, *extra_args)
                measure_data = {(f'{k}_among_{malnourishment_state}_in_age_group_{age_group}'
                                 f'_treatment_group_{treatment_group}'): v
                                for k, v in measure_data.items()}
                metrics.update(measure_data)

        the_living = pop[(pop.alive == 'alive') & pop.tracked]
        the_dead = pop[pop.alive == 'dead']
        metrics['years_of_life_lost'] = self.life_expectancy(the_dead.index).sum()
        metrics['total_population_living'] = len(the_living)
        metrics['total_population_dead'] = len(the_dead)

        return metrics
