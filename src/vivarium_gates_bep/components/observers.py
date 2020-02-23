from collections import Counter
from itertools import product

import pandas as pd
from vivarium_public_health.metrics import (MortalityObserver as MortalityObserver_,
                                            DisabilityObserver as DisabilityObserver_)
from vivarium_public_health.metrics.utilities import (get_output_template, get_group_counts,
                                                      QueryString, to_years, get_person_time,
                                                      get_deaths, get_years_of_life_lost,
                                                      get_years_lived_with_disability)

from vivarium_gates_bep import globals as project_globals


class MortalityObserver(MortalityObserver_):

    def setup(self, builder):
        super().setup(builder)
        columns_required = ['tracked', 'alive', 'entrance_time', 'exit_time', 'cause_of_death',
                            'years_of_life_lost', 'age', project_globals.MOTHER_NUTRITION_STATUS_COLUMN,
                            project_globals.SCENARIO_COLUMN]
        if self.config.by_sex:
            columns_required += ['sex']
        self.age_bins = get_age_bins()
        # Overwrites attribute set in parent class
        self.population_view = builder.population.get_view(columns_required)

    def metrics(self, index, metrics):
        pop = self.population_view.get(index)
        pop.loc[pop.exit_time.isnull(), 'exit_time'] = self.clock()

        measure_getters = (
            (get_person_time, ()),
            (get_deaths, (project_globals.CAUSES_OF_DEATH,)),
            (get_years_of_life_lost, (self.life_expectancy, project_globals.CAUSES_OF_DEATH)),
        )

        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]
            base_args = (pop_in_group, self.config.to_dict(), self.start_time, self.clock(), self.age_bins)

            for measure_getter, extra_args in measure_getters:
                measure_data = measure_getter(*base_args, *extra_args)
                measure_data = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                                for k, v in measure_data.items()}
                metrics.update(measure_data)

        the_living = pop[(pop.alive == 'alive') & pop.tracked]
        the_dead = pop[pop.alive == 'dead']
        metrics[project_globals.TOTAL_YLLS_COLUMN] = self.life_expectancy(the_dead.index).sum()
        metrics['total_population_living'] = len(the_living)
        metrics['total_population_dead'] = len(the_dead)

        return metrics


class DisabilityObserver(DisabilityObserver_):
    def setup(self, builder):
        super().setup(builder)
        self.age_bins = get_age_bins()

        columns_required = ['tracked', 'alive', 'years_lived_with_disability',
                            project_globals.MOTHER_NUTRITION_STATUS_COLUMN,
                            project_globals.SCENARIO_COLUMN]
        if self.config.by_age:
            columns_required += ['age']
        if self.config.by_sex:
            columns_required += ['sex']
        # Overwrites attribute set in parent class
        self.population_view = builder.population.get_view(columns_required)
        # Overwrites attribute set in parent class
        self.disability_weight_pipelines = {k: v for k, v in self.disability_weight_pipelines.items()
                                            if k in project_globals.CAUSES_OF_DISABILITY}

    def on_time_step_prepare(self, event):
        pop = self.population_view.get(event.index, query='tracked == True and alive == "alive"')
        self.update_metrics(pop)

        pop.loc[:, project_globals.TOTAL_YLDS_COLUMN] += self.disability_weight(pop.index)
        self.population_view.update(pop)

    def update_metrics(self, pop):
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]

            ylds_this_step = get_years_lived_with_disability(pop_in_group, self.config.to_dict(),
                                                             self.clock().year, self.step_size(),
                                                             self.age_bins, self.disability_weight_pipelines,
                                                             project_globals.CAUSES_OF_DISABILITY)
            ylds_this_step = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                              for k, v in ylds_this_step.items()}
            self.years_lived_with_disability.update(ylds_this_step)


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
        self.age_bins = get_age_bins()
        self.counts = Counter()
        self.person_time = Counter()

        self.states = project_globals.DISEASE_MODEL_MAP[self.disease]['states']
        self.transitions = project_globals.DISEASE_MODEL_MAP[self.disease]['transitions']

        self.previous_state_column = f'previous_{self.disease}'
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.previous_state_column])

        columns_required = ['alive', f'{self.disease}', self.previous_state_column,
                            project_globals.MOTHER_NUTRITION_STATUS_COLUMN,
                            project_globals.SCENARIO_COLUMN]
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
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]

            for state in self.states:
                state_person_time_this_step = get_state_person_time(pop_in_group, self.config, self.disease, state,
                                                                    self.clock().year, event.step_size, self.age_bins)
                state_person_time_this_step = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                                               for k, v in state_person_time_this_step.items()}
                self.person_time.update(state_person_time_this_step)

        # This enables tracking of transitions between states
        prior_state_pop = self.population_view.get(event.index)
        prior_state_pop[self.previous_state_column] = prior_state_pop[self.disease]
        self.population_view.update(prior_state_pop)

    def on_collect_metrics(self, event):
        pop = self.population_view.get(event.index)
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]

            for transition in self.transitions:
                transition_counts_this_step = get_transition_count(pop_in_group, self.config, self.disease, transition,
                                                                   event.time, self.age_bins)
                transition_counts_this_step = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                                               for k, v in transition_counts_this_step.items()}
                self.counts.update(transition_counts_this_step)

    def metrics(self, index, metrics):
        metrics.update(self.counts)
        metrics.update(self.person_time)
        return metrics

    def __repr__(self):
        return f"DiseaseObserver({self.disease})"


class ChildGrowthFailureObserver():

    @property
    def name(self):
        return f'risk_observer.child_growth_failure'

    def setup(self, builder):
        self.wasting = builder.value.get_value(f'{project_globals.WASTING_MODEL_NAME}.exposure')
        self.stunting = builder.value.get_value(f'{project_globals.STUNTING_MODEL_NAME}.exposure')

        self.record_age = 0.5  # years
        self.results = self.get_results_template()
        self.population_view = builder.population.get_view(['age', 'sex',
                                                            project_globals.MOTHER_NUTRITION_STATUS_COLUMN,
                                                            project_globals.SCENARIO_COLUMN],
                                                           query='alive == "alive"')

        builder.event.register_listener('collect_metrics', self.on_collect_metrics)
        builder.value.register_value_modifier('metrics', self.metrics)

    def on_collect_metrics(self, event):
        pop = self.population_view.get(event.index)
        pop = pop[(self.record_age <= pop.age) & (pop.age < self.record_age + to_years(event.step_size))]
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]

            stats = self.get_cgf_stats(pop_in_group)
            stats = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                     for k, v in stats.items()}
            self.results.update(stats)

    def get_results_template(self):
        stats = {}
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            suffix = f'mother_{mother_cat}_treatment_{treatment}'
            stats[f'wasting_z_score_mean_at_six_months_{suffix}'] = 0
            stats[f'wasting_z_score_sd_at_six_months_{suffix}'] = 0
            stats[f'stunting_z_score_mean_at_six_months_{suffix}'] = 0
            stats[f'stunting_z_score_sd_at_six_months_{suffix}'] = 0
            for cat in ['cat1', 'cat2', 'cat3', 'cat4']:
                stats[f'wasting_{cat}_exposed_at_six_months_{suffix}'] = 0
                stats[f'stunting_{cat}_exposed_at_six_months_{suffix}'] = 0

        return stats

    def get_cgf_stats(self, pop):
        stats = {}
        if not pop.empty:
            pop = pop.drop(columns='age')
            pop['wasting_z'] = self.wasting(pop.index, skip_post_processor=True)
            pop['wasting_cat'] = self.wasting(pop.index)
            pop['stunting_z'] = self.stunting(pop.index, skip_post_processor=True)
            pop['stunting_cat'] = self.stunting(pop.index)

            stats[f'wasting_z_score_mean_at_six_months'] = pop.wasting_z.mean()
            stats[f'wasting_z_score_sd_at_six_months'] = pop.wasting_z.std()
            stats[f'stunting_z_score_mean_at_six_months'] = pop.wasting_z.mean()
            stats[f'stunting_z_score_sd_at_six_months'] = pop.wasting_z.std()
            for cat, value in dict(pop.wasting_cat.value_counts()).items():
                stats[f'wasting_{cat}_exposed_at_six_months'] = value
            for cat, value in dict(pop.stunting_cat.value_counts()).items():
                stats[f'stunting_{cat}_exposed_at_six_months'] = value
        return stats

    def metrics(self, index, metrics):
        metrics.update(self.results)
        return metrics


class LBWSGObserver:

    @property
    def name(self):
        return f'risk_observer.low_birth_weight_and_short_gestation'

    def setup(self, builder):
        value_key = 'low_birth_weight_and_short_gestation.exposure'
        self.lbwsg = builder.value.get_value(value_key)
        builder.value.register_value_modifier('metrics', self.metrics)
        self.results = {}
        columns = ['sex', project_globals.MOTHER_NUTRITION_STATUS_COLUMN, project_globals.SCENARIO_COLUMN]
        self.population_view = builder.population.get_view(columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 requires_columns=columns,
                                                 requires_values=[value_key])

    def on_initialize_simulants(self, pop_data):
        pop = self.population_view.get(pop_data.index)
        raw_exposure = self.lbwsg(pop_data.index, skip_post_processor=True)
        exposure = self.lbwsg(pop_data.index)
        pop = pd.concat([pop, raw_exposure, exposure], axis=1)
        categories = product(project_globals.MOTHER_NUTRITION_CATEGORIES, project_globals.TREATMENTS)
        for mother_cat, treatment in categories:
            pop_in_group = pop.loc[(pop[project_globals.MOTHER_NUTRITION_STATUS_COLUMN] == mother_cat)
                                   & (pop[project_globals.SCENARIO_COLUMN] == treatment)]
            stats = self.get_lbwsg_stats(pop_in_group)
            stats = {f'{k}_mother_{mother_cat}_treatment_{treatment}': v
                     for k, v in stats.items()}
            self.results.update(stats)

    def get_lbwsg_stats(self, pop):
        stats = {'birth_weight_mean': 0,
                 'birth_weight_sd': 0,
                 'birth_weight_proportion_below_2500g': 0,
                 'gestational_age_mean': 0,
                 'gestational_age_sd': 0,
                 'gestational_age_proportion_below_37w': 0}
        if not pop.empty:
            stats[f'birth_weight_mean'] = pop.birth_weight.mean()
            stats[f'birth_weight_sd'] = pop.birth_weight.std()
            stats[f'birth_weight_proportion_below_2500g'] = (
                    len(pop[pop.birth_weight < project_globals.UNDERWEIGHT]) / len(pop)
            )
            stats[f'gestational_age_mean'] = pop.gestation_time.mean()
            stats[f'gestational_age_sd'] = pop.gestation_time.std()
            stats[f'gestational_age_proportion_below_37w'] = (
                    len(pop[pop.gestation_time < project_globals.PRETERM]) / len(pop)
            )
        return stats

    def metrics(self, index, metrics):
        metrics.update(self.results)
        return metrics


def get_state_person_time(pop, config, disease, state, current_year, step_size, age_bins):
    """Custom person time getter that handles state column name assumptions"""
    base_key = get_output_template(**config).substitute(measure=f'{state}_person_time',
                                                        year=current_year)
    base_filter = QueryString(f'alive == "alive" and {disease} == "{state}"')
    person_time = get_group_counts(pop, base_filter, base_key, config, age_bins,
                                   aggregate=lambda x: len(x) * to_years(step_size))
    return person_time


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


def get_prevalent_at_birth_count(pop, config, disease, state, age_bins):
    config = config.copy()
    config.update({'by_year': False, 'by_age': False})
    base_key = get_output_template(**config).substitute(measure=f'{state}_prevalent_count_at_birth')
    base_filter = QueryString(f'{disease} == "{state}"')
    prevalent_count = get_group_counts(pop, base_filter, base_key, config, age_bins)
    return prevalent_count


def get_age_bins():
    return pd.DataFrame({
        'age_start': [0.,       0.019178, 0.076712, 0.5, 1.],
        'age_end':   [0.019178, 0.076712, 0.5,      1.,  4.],
        'age_group_name': ['Early Neonatal', 'Late Neonatal', '1mo to 6mo', '6mo to 1', '1 to 4']
    })
