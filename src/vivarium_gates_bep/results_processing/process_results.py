from pathlib import Path
from typing import NamedTuple, List

import pandas as pd
import yaml

from vivarium_gates_bep import globals as project_globals


SCENARIO_COLUMN = 'scenario'
GROUPBY_COLUMNS = [project_globals.INPUT_DRAW_COLUMN, SCENARIO_COLUMN]
PERSON_YEAR_SCALE = 100_000
DROP_COLUMNS = ['measure']
SHARED_COLUMNS = ['age_group', 'treatment_group', 'mother_status', 'input_draw', 'scenario']


def make_measure_data(data):
    measure_data = MeasureData(
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
    return measure_data


def make_final_data(measure_data):
    final_data = FinalData(
        mortality_rate=get_rate_data(measure_data, 'deaths', 'mortality_rate'),
        ylls=get_rate_data(measure_data, 'ylls', 'ylls'),
        ylds=get_rate_data(measure_data, 'ylds', 'ylds'),
        dalys=get_dalys(measure_data),
        proportion_underweight=measure_data.birth_weight[measure_data.birth_weight.measure == 'proportion_below_2500g']
    )
    return final_data


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


class FinalData(NamedTuple):
    mortality_rate: pd.DataFrame
    ylls: pd.DataFrame
    ylds: pd.DataFrame
    dalys: pd.DataFrame
    proportion_underweight: pd.DataFrame

    def dump(self, output_dir: Path):
        for key, df in self._asdict().items():
            df.to_hdf(output_dir / f'{key}.hdf', key=key)
            df.to_csv(output_dir / f'{key}.csv')


def read_data(path: Path) -> (pd.DataFrame, List[str]):
    data = pd.read_hdf(path)
    data = (data
            .drop(columns=project_globals.THROWAWAY_COLUMNS)
            .reset_index(drop=True)
            .rename(columns={project_globals.OUTPUT_SCENARIO_COLUMN: SCENARIO_COLUMN}))
    data[project_globals.INPUT_DRAW_COLUMN] = data[project_globals.INPUT_DRAW_COLUMN].astype(int)
    data[project_globals.RANDOM_SEED_COLUMN] = data[project_globals.RANDOM_SEED_COLUMN].astype(int)
    with (path.parent / 'keyspace.yaml').open() as f:
        keyspace = yaml.full_load(f)
    return data, keyspace


def filter_out_incomplete(data, keyspace):
    for draw in keyspace[project_globals.INPUT_DRAW_COLUMN]:
        # For each draw, gather all random seeds completed for all scenarios.
        random_seeds = set(keyspace[project_globals.RANDOM_SEED_COLUMN])
        for scenario in keyspace[project_globals.OUTPUT_SCENARIO_COLUMN]:
            seeds_in_data = data.loc[(data[project_globals.INPUT_DRAW_COLUMN] == draw)
                                     & (data[SCENARIO_COLUMN]) == scenario,
                                     project_globals.RANDOM_SEED_COLUMN].unique()
            random_seeds = random_seeds.intersection(seeds_in_data)
        import pdb; pdb.set_trace()

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


def get_rate_numerator(measure_data: MeasureData, numerator_label: str):
    numerator = getattr(measure_data, numerator_label).drop(columns=DROP_COLUMNS)
    all_cause_numerator = numerator.groupby(SHARED_COLUMNS).value.sum().reset_index()
    all_cause_numerator['cause'] = 'all_causes'
    return pd.concat([numerator, all_cause_numerator], ignore_index=True).set_index(SHARED_COLUMNS + ['cause'])


def compute_rate(measure_data: MeasureData, numerator: pd.DataFrame, measure: str):
    person_time = measure_data.person_time.drop(columns=DROP_COLUMNS).set_index(SHARED_COLUMNS)
    rate_data = (numerator / person_time * PERSON_YEAR_SCALE).fillna(0).reset_index()
    rate_data['measure'] = f'{measure}_per_100k_py'
    return rate_data


def get_rate_data(measure_data: MeasureData, numerator_label: str, measure: str) -> pd.DataFrame:
    numerator = get_rate_numerator(measure_data, numerator_label)
    rate_data = compute_rate(measure_data, numerator, measure)
    return sort_data(rate_data)


def get_dalys(measure_data: MeasureData):
    ylls = get_rate_numerator(measure_data, 'ylls')
    ylds = get_rate_numerator(measure_data, 'ylds')
    ylls.loc[ylds.index] += ylds
    dalys = compute_rate(measure_data, ylls, 'dalys')
    return sort_data(dalys)
