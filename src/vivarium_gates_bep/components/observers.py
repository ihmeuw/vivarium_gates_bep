from vivarium_public_health.metrics import MortalityObserver, DisabilityObserver
from vivarium_public_health.metrics.utilities import (
    get_years_lived_with_disability,
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

        for malnourishment_category, age_group, treatment_group in project_globals.STRATIFICATION_GROUPS:
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


class BEPGatesDisabilityObserver(DisabilityObserver):

    def __init__(self):
        super().__init__()

    def setup(self, builder):
        super().setup(builder)
        self.malnourishment = builder.value.get_value(f'maternal_malnourishment.exposure')
        self.treatment_group = builder.value.get_value('treatment.exposure')
        self.disability_weight_pipelines = {k: v for k, v in self.disability_weight_pipelines.items()
                                            if k in project_globals.CAUSES_OF_DISABILITY}

    def on_time_step_prepare(self, event):
        pop = self.population_view.get(event.index, query='tracked == True and alive == "alive"')

        self.update_metrics(pop)

        pop.loc[:, 'years_lived_with_disability'] += self.disability_weight(pop.index)
        self.population_view.update(pop)

    def update_metrics(self, pop):
        # TODO uncomment this once the pipelines have been created
        # pop_malnourishment_category = self.malnourishment(pop.index)
        # pop_treatment_group = self.treatment_group(pop.index)

        for malnourishment_category, age_group, treatment_group in project_globals.STRATIFICATION_GROUPS:
            malnourishment_state = project_globals.MALNOURISHMENT_MAP[malnourishment_category]
            # TODO uncomment this once the pipelines have been created
            # pop_in_group = pop.loc[
            #     pop_malnourishment_category == malnourishment_category
            #     & pop_treatment_group == treatment_group
            # ]
            #
            # ylds_this_step = get_years_lived_with_disability(
            #     pop_in_group, self.config.to_dict(), self.clock().year, self.step_size(), self.age_bins,
            #     self.disability_weight_pipelines, project_globals.CAUSES_OF_DISABILITY
            # )
            ylds_this_step = get_years_lived_with_disability(
                pop, self.config.to_dict(), self.clock().year, self.step_size(), self.age_bins,
                self.disability_weight_pipelines, project_globals.CAUSES_OF_DISABILITY
            )
            ylds_this_step = {(f'{k}_among_{malnourishment_state}_in_age_group_{age_group}'
                               f'_treatment_group_{treatment_group}'): v
                              for k, v in ylds_this_step.items()}
            self.years_lived_with_disability.update(ylds_this_step)


class BEPGatesMockObserver():
    '''
    Adds columns to ensure a complete output shell
    '''
    @property
    def name(self):
        return 'mock_observer'

    def __init__(self):
        # As working observers are completed add the appropriate key to exclude the mocking behavior
        exclude_list = [
            'person_time',  # BEPGatesMortalityObserver
            'death',        # BEPGatesMortalityObserver
            'ylls',         # BEPGatesMortalityObserver
            'ylds',         # BEPGatesDisabilityObserver
        ]
        need_to_mock = [i for i in list(project_globals.COLUMN_TEMPLATES.keys()) if i not in exclude_list]
        mock_columns = []
        for col in need_to_mock:
            mock_columns.extend(project_globals.result_columns(col))
        self.mocks = {i: project_globals.MOCKED_COLUMN_VALUE for i in mock_columns}

    def setup(self, builder):
        builder.value.register_value_modifier('metrics', self.metrics)

    def metrics(self, index, metrics):
        metrics.update(self.mocks)
        return metrics
