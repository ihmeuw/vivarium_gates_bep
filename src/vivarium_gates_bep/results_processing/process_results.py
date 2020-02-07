from pathlib import Path
from typing import NamedTuple

import pandas as pd

from vivarium_gates_bep import globals as project_globals


SCENARIO_COLUMN = 'scenario'
GROUPBY_COLUMNS = [project_globals.INPUT_DRAW_COLUMN, SCENARIO_COLUMN]


def make_measure_data(data):
    count_data = MeasureData(
        population=get_population_data(data),
        person_time=get_measure_data(data, 'person_time', with_cause=False),
        ylls=get_measure_data(data, 'ylls'),
        ylds=get_measure_data(data, 'ylds'),
        deaths=get_measure_data(data, 'deaths'),
        state_person_time=get_measure_data(data, 'state_person_time', with_cause=False),
        transition_count=get_measure_data(data, 'transition_count', with_cause=False),
        birth_prevalence=get_nn_birth_prevalence(data),
        cgf_z_scores=get_z_scores(data),
        cgf_categories=get_risk_categories(data),
        birth_weight=get_lbwsg_data(data, 'birth_weight'),
        gestational_age=get_lbwsg_data(data, 'gestational_age')
    )
    return count_data


class MeasureData(NamedTuple):
    population: pd.DataFrame
    person_time: pd.DataFrame
    ylls: pd.DataFrame
    ylds: pd.DataFrame
    deaths: pd.DataFrame
    state_person_time: pd.DataFrame
    transition_count: pd.DataFrame
    birth_prevalence: pd.DataFrame
    cgf_z_scores: pd.DataFrame
    cgf_categories: pd.DataFrame
    birth_weight: pd.DataFrame
    gestational_age: pd.DataFrame

    def dump(self, output_dir: Path):
        for key, df in self._asdict().items():
            df.to_hdf(output_dir / f'{key}.hdf', key=key)
            df.to_csv(output_dir / f'{key}.csv')


def read_data(path: str) -> pd.DataFrame:
    data = pd.read_hdf(path)
    data = (data
            .drop(columns=project_globals.THROWAWAY_COLUMNS + [project_globals.RANDOM_SEED_COLUMN])
            .reset_index(drop=True)
            .rename(columns={project_globals.OUTPUT_SCENARIO_COLUMN: SCENARIO_COLUMN}))
    return data


def aggregate_over_seed(data):
    non_count_columns = []
    for non_count_template in project_globals.NON_COUNT_TEMPLATES:
        non_count_columns += project_globals.RESULT_COLUMNS(non_count_template)
    count_columns = [c for c in data.columns if c not in non_count_columns + GROUPBY_COLUMNS]

    non_count_data = data[non_count_columns + GROUPBY_COLUMNS].groupby(GROUPBY_COLUMNS).mean()
    count_data = data[count_columns + GROUPBY_COLUMNS].groupby(GROUPBY_COLUMNS).sum()
    return pd.concat([count_data, non_count_data], axis=1).reset_index()


def pivot_data(data):
    return (data
            .set_index(GROUPBY_COLUMNS)
            .stack()
            .reset_index()
            .rename(columns={'level_2': 'process', 0: 'value'}))


def sort_data(data):
    sort_order = ['age_group', 'risk', 'cause', 'treatment_group', 'mother_status', 'measure', 'input_draw']
    sort_order = [c for c in sort_order if c in data.columns]
    other_cols = [c for c in data.columns if c not in sort_order]
    data = data[sort_order + other_cols].sort_values(sort_order)
    return data.reset_index(drop=True)


def split_processing_column(data, with_cause):
    if with_cause:
        data['measure'], data['process'] = data.process.str.split('_due_to_').str
        data['cause'], data['process'] = data.process.str.split('_in_age_group_').str
    else:
        data['measure'], data['process'] = data.process.str.split('_in_age_group_').str
    data['age_group'], data['process'] = data.process.str.split('_mother_').str
    data['mother_status'], data['treatment_group'] = data.process.str.split('_treatment_').str
    return data.drop(columns='process')


def get_population_data(data):
    total_pop = pivot_data(data[[project_globals.TOTAL_POPULATION_COLUMN]
                                + project_globals.RESULT_COLUMNS('population')
                                + GROUPBY_COLUMNS])
    total_pop = total_pop.rename(columns={'process': 'measure'})
    total_pop['treatment_group'] = 'all'
    total_pop['mother_status'] = 'all'
    stratified_pop = pivot_data(data[project_globals.RESULT_COLUMNS('population_stratified')
                                     + GROUPBY_COLUMNS])
    stratified_pop['measure'], stratified_pop['process'] = stratified_pop.process.str.split('_mother_').str
    stratified_pop['mother_status'], stratified_pop['treatment_group'] = stratified_pop.process.str.split('_treatment_').str
    stratified_pop = stratified_pop.drop(columns='process')
    return sort_data(pd.concat([total_pop, stratified_pop], ignore_index=True))


def get_measure_data(data, measure, with_cause=True):
    data = pivot_data(data[project_globals.RESULT_COLUMNS(measure) + GROUPBY_COLUMNS])
    data = split_processing_column(data, with_cause)
    return sort_data(data)


def get_nn_birth_prevalence(data):
    data = pivot_data(data[project_globals.RESULT_COLUMNS('birth_prevalence') + GROUPBY_COLUMNS])
    data['measure'] = 'neonatal_birth_prevalence'
    data['process'] = data.process.str.split('_mother_').str[1]
    data['mother_status'], data['treatment_group'] = data.process.str.split('_treatment_').str
    data = data.drop(columns='process')
    return sort_data(data)


def get_z_scores(data):
    data = pivot_data(data[project_globals.RESULT_COLUMNS('z_scores') + GROUPBY_COLUMNS])
    data['risk'], data['process'] = data.process.str.split('_z_score_').str
    data['measure'], data['process'] = data.process.str.split('_at_six_months_mother_').str
    data['mother_status'], data['treatment_group'] = data.process.str.split('_treatment_').str
    data = data.drop(columns='process')
    return sort_data(data)


def get_risk_categories(data):
    data = pivot_data(data[project_globals.RESULT_COLUMNS('category_counts') + GROUPBY_COLUMNS])
    data['risk'], data['process'] = data.process.str.split('_cat').str
    data['measure'], data['process'] = data.process.str.split('_exposed_at_six_months_mother_').str
    data['measure'] = data['measure'].apply(lambda x: f'cat{x}')
    data['mother_status'], data['treatment_group'] = data.process.str.split('_treatment_').str
    data = data.drop(columns='process')
    return sort_data(data)


def get_lbwsg_data(data, risk):
    data = pivot_data(data[project_globals.RESULT_COLUMNS(risk) + GROUPBY_COLUMNS])
    data['risk'] = risk
    data['measure'], data['process'] = data.process.str.split(f'{risk}_').str[1].str.split('_mother_').str
    data['mother_status'], data['treatment_group'] = data.process.str.split('_treatment_').str
    data = data.drop(columns='process')
    return sort_data(data)
