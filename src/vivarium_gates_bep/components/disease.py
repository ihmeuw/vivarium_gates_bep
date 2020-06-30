import pandas as pd
from vivarium_public_health.disease import (DiseaseModel as DiseaseModel_, SusceptibleState,
                                            DiseaseState, RecoveredState)


class DiseaseModel(DiseaseModel_):

    def on_initialize_simulants(self, pop_data):
        population = self.population_view.subview(['age', 'sex']).get(pop_data.index)
        state_names, weights_bins = self.get_state_weights(pop_data.index, "birth_prevalence")

        if state_names and not population.empty:
            # only do this if there are states in the model that supply prevalence data
            population['sex_id'] = population.sex.apply({'Male': 1, 'Female': 2}.get)

            condition_column = self.assign_initial_status_to_simulants(population, state_names, weights_bins,
                                                                       self.randomness.get_draw(population.index))

            condition_column = condition_column.rename(columns={'condition_state': self.state_column})
        else:
            condition_column = pd.Series(self.initial_state, index=population.index, name=self.state_column)
        self.population_view.update(condition_column)


def SIS(cause: str) -> DiseaseModel:
    healthy = SusceptibleState(cause)
    infected = DiseaseState(cause)

    healthy.allow_self_transitions()
    healthy.add_transition(infected, source_data_type='rate')
    infected.allow_self_transitions()
    infected.add_transition(healthy, source_data_type='rate')

    return DiseaseModel(cause, states=[healthy, infected])


def SIR_fixed_duration(cause: str, duration: str) -> DiseaseModel:
    duration = pd.Timedelta(days=float(duration) // 1, hours=(float(duration) % 1) * 24.0)

    healthy = SusceptibleState(cause)
    infected = DiseaseState(cause, get_data_functions={'dwell_time': lambda _, __: duration})
    recovered = RecoveredState(cause)

    healthy.allow_self_transitions()
    healthy.add_transition(infected, source_data_type='rate')
    infected.add_transition(recovered)
    infected.allow_self_transitions()
    recovered.allow_self_transitions()

    return DiseaseModel(cause, states=[healthy, infected, recovered])


def NeonatalSIS(cause):
    with_condition_data_functions = {'birth_prevalence':
                                     lambda cause, builder: builder.data.load(f"cause.{cause}.birth_prevalence")}

    healthy = SusceptibleState(cause)
    with_condition = DiseaseState(cause, get_data_functions=with_condition_data_functions)

    healthy.allow_self_transitions()
    healthy.add_transition(with_condition, source_data_type='rate')
    with_condition.allow_self_transitions()
    with_condition.add_transition(healthy, source_data_type='rate')

    # TODO: LSFF uses default VPH disease model, should this be different?
    return DiseaseModel_(cause, states=[healthy, with_condition])