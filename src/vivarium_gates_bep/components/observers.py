from collections import Counter

import pandas as pd
from vivarium_public_health.metrics.utilities import (get_age_bins, get_output_template, get_group_counts,
                                                      QueryString, to_years)

from vivarium_gates_bep import globals as project_globals


class DiseaseObserver:
    """Observes disease counts, person time, and prevalent cases for a cause.

    By default, this observer computes aggregate susceptible person time
    and counts of disease cases over the entire simulation.  It can be
    configured to bin these into age_groups, sexes, and years by setting
    the ``by_age``, ``by_sex``, and ``by_year`` flags, respectively.

    It also records prevalent cases on a particular sample date each year.
    These will also be binned based on the flags set for the observer.
    Additionally, the sample date is configurable and defaults to July 1st
    of each year.

    In the model specification, your configuration for this component should
    be specified as, e.g.:

    .. code-block:: yaml

        configuration:
            metrics:
                {YOUR_DISEASE_NAME}_observer:
                    by_age: True
                    by_year: False
                    by_sex: True
                    prevalence_sample_date:
                        month: 4
                        day: 10

    """
    configuration_defaults = {
        'metrics': {
            'disease_observer': {
                'by_age': False,
                'by_year': False,
                'by_sex': False,
            }
        }
    }

    def __init__(self, disease: str):
        self.disease = disease
        self.configuration_defaults = {
            'metrics': {f'{disease}_observer': DiseaseObserver.configuration_defaults['metrics']['disease_observer']}
        }

    @property
    def name(self):
        return f'disease_observer.{self.disease}'

    def setup(self, builder):
        self.config = builder.configuration['metrics'][f'{self.disease}_observer'].to_dict()
        self.clock = builder.time.clock()
        self.age_bins = get_age_bins(builder)
        self.counts = Counter()
        self.person_time = Counter()

        self.states = project_globals.DISEASE_MODEL_MAP[self.disease]['states']
        self.transitions = project_globals.DISEASE_MODEL_MAP[self.disease]['transitions']

        self.previous_state_column = f'previous_{self.disease}'
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.previous_state_column])

        columns_required = ['alive', f'{self.disease}', self.previous_state_column]
        for state in self.states:
            columns_required.append(f'{state}_event_time')

        if self.config['by_age']:
            columns_required += ['age']
        if self.config['by_sex']:
            columns_required += ['sex']
        self.population_view = builder.population.get_view(columns_required)

        builder.value.register_value_modifier('metrics', self.metrics)
        # FIXME: The state table is modified before the clock advances.
        # In order to get an accurate representation of person time we need to look at
        # the state table before anything happens.
        builder.event.register_listener('time_step__prepare', self.on_time_step_prepare)
        builder.event.register_listener('collect_metrics', self.on_collect_metrics)

    def on_initialize_simulants(self, pop_data):
        self.population_view.update(pd.Series('', index=pop_data.index, name=self.previous_state_column))

    def on_time_step_prepare(self, event):
        pop = self.population_view.get(event.index)
        # Ignoring the edge case where the step spans a new year.
        # Accrue all counts and time to the current year.
        for state in self.states:
            state_person_time_this_step = self.get_state_person_time(pop, self.config, self.disease, state,
                                                                     self.clock().year, event.step_size, self.age_bins)
            self.person_time.update(state_person_time_this_step)

        # This enables tracking of transitions between states
        prior_state_pop = self.population_view.get(event.index)
        prior_state_pop[self.previous_state_column] = prior_state_pop[self.disease]
        self.population_view.update(prior_state_pop)

    def on_collect_metrics(self, event):
        pop = self.population_view.get(event.index)
        for transition in self.transitions:
            transition_counts_this_step = self.get_transition_count(pop, self.config, self.disease, transition,
                                                                    event.time, self.age_bins)
            self.counts.update(transition_counts_this_step)

    def metrics(self, index, metrics):
        metrics.update(self.counts)
        metrics.update(self.person_time)
        return metrics

    @staticmethod
    def get_state_person_time(pop, config, disease, state, current_year, step_size, age_bins):
        """Custom person time getter that handles state column name assumptions"""
        base_key = get_output_template(**config).substitute(measure=f'{state}_person_time',
                                                            year=current_year)
        base_filter = QueryString(f'alive == "alive" and {disease} == "{state}"')
        person_time = get_group_counts(pop, base_filter, base_key, config, age_bins,
                                       aggregate=lambda x: len(x) * to_years(step_size))
        return person_time

    @staticmethod
    def get_transition_count(pop, config, disease, transition, event_time, age_bins):
        from_state, to_state = transition.split('_TO_')
        event_this_step = ((pop[f'{to_state}_event_time'] == event_time)
                           & (pop[f'previous_{disease}'] == from_state))
        transitioned_pop = pop.loc[event_this_step]
        base_key = get_output_template(**config).substitute(measure=f'{transition}_event_count',
                                                            year=event_time.year)
        base_filter = QueryString('')
        transition_count = get_group_counts(transitioned_pop, base_filter, base_key, config, age_bins)
        return transition_count

    def __repr__(self):
        return f"DiseaseObserver({self.disease})"
