"""Loads, standardizes and validates input data for the simulation."""
from gbd_mapping import causes, risk_factors
import pandas as pd
from vivarium.framework.artifact import EntityKey
from vivarium_inputs import interface, utilities, utility_data, globals as vi_globals

from vivarium_gates_bep import paths, globals as project_globals


def get_data(lookup_key: str, location: str) -> pd.DataFrame:
    """Retrieves data from an appropriate source.

    Parameters
    ----------
    lookup_key
        The key that will eventually get put in the artifact with
        the requested data.
    location
        The location to get data for.

    Returns
    -------
        The requested data.

    """
    mapping = {
        project_globals.POPULATION_STRUCTURE: load_population_structure,
        project_globals.POPULATION_AGE_BINS: load_age_bins,
        project_globals.POPULATION_DEMOGRAPHY: load_demographic_dimensions,
        project_globals.POPULATION_TMRLE: load_theoretical_minimum_risk_life_expectancy,

        project_globals.ALL_CAUSE_CSMR: load_standard_data,

        project_globals.DIARRHEA_PREVALENCE: load_standard_data,
        project_globals.DIARRHEA_INCIDENCE_RATE: load_standard_data,
        project_globals.DIARRHEA_REMISSION_RATE: load_standard_data,
        project_globals.DIARRHEA_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.DIARRHEA_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.DIARRHEA_DISABILITY_WEIGHT: load_standard_data,
        project_globals.DIARRHEA_RESTRICTIONS: load_standard_data,

        project_globals.MEASLES_PREVALENCE: load_standard_data,
        project_globals.MEASLES_INCIDENCE_RATE: load_standard_data,
        project_globals.MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_DISABILITY_WEIGHT: load_standard_data,
        project_globals.MEASLES_RESTRICTIONS: load_standard_data,

        project_globals.LRI_PREVALENCE: load_standard_data,
        project_globals.LRI_INCIDENCE_RATE: load_standard_data,
        project_globals.LRI_REMISSION_RATE: load_standard_data,
        project_globals.LRI_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_DISABILITY_WEIGHT: load_standard_data,
        project_globals.LRI_RESTRICTIONS: load_standard_data,

        project_globals.MENINGITIS_PREVALENCE: load_standard_data,
        project_globals.MENINGITIS_INCIDENCE_RATE: load_standard_data,
        project_globals.MENINGITIS_REMISSION_RATE: load_standard_data,
        project_globals.MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MENINGITIS_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.MENINGITIS_DISABILITY_WEIGHT: load_meningitis_disability_weight,
        project_globals.MENINGITIS_RESTRICTIONS: load_standard_data,

        project_globals.PEM_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_DISABILITY_WEIGHT: load_standard_data,
        project_globals.PEM_RESTRICTIONS: load_standard_data,

        project_globals.NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_PREVALENCE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_BIRTH_PREVALENCE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_DISABILITY_WEIGHT: load_standard_data,
        project_globals.NEONATAL_DISORDERS_RESTRICTIONS: load_standard_data,

        project_globals.WASTING_DISTRIBUTION: load_standard_data,
        project_globals.WASTING_ALT_DISTRIBUTION: load_standard_data,
        project_globals.WASTING_CATEGORIES: load_standard_data,
        project_globals.WASTING_EXPOSURE_MEAN: load_standard_data,
        project_globals.WASTING_EXPOSURE_SD: load_standard_data,
        project_globals.WASTING_EXPOSURE_WEIGHTS: load_standard_data,
        project_globals.WASTING_RELATIVE_RISK: load_standard_data,
        project_globals.WASTING_PAF: load_standard_data,

        project_globals.STUNTING_DISTRIBUTION: load_standard_data,
        project_globals.STUNTING_ALT_DISTRIBUTION: load_standard_data,
        project_globals.STUNTING_CATEGORIES: load_standard_data,
        project_globals.STUNTING_EXPOSURE_MEAN: load_standard_data,
        project_globals.STUNTING_EXPOSURE_SD: load_standard_data,
        project_globals.STUNTING_EXPOSURE_WEIGHTS: load_standard_data,
        project_globals.STUNTING_RELATIVE_RISK: load_standard_data,
        project_globals.STUNTING_PAF: load_standard_data,

        project_globals.LBWSG_DISTRIBUTION: load_standard_data,
        project_globals.LBWSG_CATEGORIES: load_standard_data,
        project_globals.LBWSG_EXPOSURE: load_lbwsg_exposure,
        project_globals.LBWSG_RELATIVE_RISK: load_lbwsg_relative_risk,
        project_globals.LBWSG_PAF: load_lbwsg_paf,

    }
    return mapping[lookup_key](lookup_key, location)


def load_population_structure(key: str, location: str) -> pd.DataFrame:
    return interface.get_population_structure(location)


def load_age_bins(key: str, location: str) -> pd.DataFrame:
    return interface.get_age_bins()


def load_demographic_dimensions(key: str, location: str) -> pd.DataFrame:
    return interface.get_demographic_dimensions(location)


def load_theoretical_minimum_risk_life_expectancy(key: str, location: str) -> pd.DataFrame:
    return interface.get_theoretical_minimum_risk_life_expectancy()


def load_standard_data(key: str, location: str) -> pd.DataFrame:
    key = EntityKey(key)
    return interface.get_measure(causes[key.name], key.measure, location)


def load_meningitis_disability_weight(key: str, location: str) -> pd.DataFrame:
    key = EntityKey(key)
    meningitis = causes[key.name]
    sub_cause_dws = []
    for subcause in meningitis.sub_causes:
        prevalence = interface.get_measure(subcause, 'prevalence', location)
        disability = interface.get_measure(subcause, 'disability_weight', location)
        sub_cause_dws.append(prevalence * disability)
    meningitis_prevalence = interface.get_measure(meningitis, 'prevalence', location)
    return sum(sub_cause_dws) / meningitis_prevalence


def load_lbwsg_exposure(key: str, location: str):

    path = paths.lbwsg_data_path('exposure', location)
    data = pd.read_hdf(path)
    # Fixme: pulled from vivarium inputs.  Probably don't need all this.
    allowable_measures = [vi_globals.MEASURES['Proportion'],
                          vi_globals.MEASURES['Continuous'],
                          vi_globals.MEASURES['Prevalence']]
    proper_measure_id = set(data.measure_id).intersection(allowable_measures)
    if len(proper_measure_id) != 1:
        raise ValueError(f'Exposure data have {len(proper_measure_id)} measure id(s). Data should have '
                         f'exactly one id out of {allowable_measures} but came back with {proper_measure_id}.')
    else:
        data = data[data.measure_id == proper_measure_id.pop()]

    data = data.drop('modelable_entity_id', 'columns')
    data = data[data.parameter != 'cat124']  # LBWSG data has an extra residual category added by get_draws.
    data = utilities.filter_data_by_restrictions(data, risk_factors.low_birth_weight_and_short_gestation,
                                                 'outer', utility_data.get_age_group_ids())
    tmrel_cat = 'cat56'
    exposed = data[data.parameter != tmrel_cat]
    unexposed = data[data.parameter == tmrel_cat]
    #  FIXME: We fill 1 as exposure of tmrel category, which is not correct.
    data = pd.concat([utilities.normalize(exposed, fill_value=0), utilities.normalize(unexposed, fill_value=1)],
                     ignore_index=True)

    # normalize so all categories sum to 1
    cols = list(set(data.columns).difference(vi_globals.DRAW_COLUMNS + ['parameter']))
    sums = data.groupby(cols)[vi_globals.DRAW_COLUMNS].sum()
    data = (data.groupby('parameter')
            .apply(lambda df: df.set_index(cols).loc[:, vi_globals.DRAW_COLUMNS].divide(sums))
            .reset_index())
    data = data.filter(vi_globals.DEMOGRAPHIC_COLUMNS + vi_globals.DRAW_COLUMNS + ['parameter'])
    data = utilities.reshape(data)
    data = utilities.scrub_gbd_conventions(data, location)
    data = utilities.split_interval(data, interval_column='age', split_column_prefix='age')
    data = utilities.split_interval(data, interval_column='year', split_column_prefix='year')
    return utilities.sort_hierarchical_data(data)


def load_lbwsg_relative_risk(key: str, location: str):
    raise NotImplementedError()


def load_lbwsg_paf(key: str, location: str):
    raise NotImplementedError()
