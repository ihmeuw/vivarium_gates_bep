"""Loads, standardizes and validates input data for the simulation."""
from get_draws.api import get_draws
from gbd_mapping import causes, risk_factors, covariates
import numpy as np
import pandas as pd
from vivarium.framework.artifact import EntityKey
from vivarium_inputs import interface, utilities, utility_data, globals as vi_globals
from vivarium_inputs.mapping_extension import alternative_risk_factors
import vivarium_inputs.validation.sim as validation

from vivarium_gates_bep import paths, globals as project_globals
from vivarium_gates_bep.tools import make_bw_risk_correlation as bw_risk


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

        project_globals.COVARIATE_LIVE_BIRTHS_BY_SEX: load_standard_data,
        project_globals.COVARIATE_ANC1_COVERAGE: load_standard_data,

        project_globals.DIARRHEA_PREVALENCE: load_standard_data,
        project_globals.DIARRHEA_INCIDENCE_RATE: load_standard_data,
        project_globals.DIARRHEA_REMISSION_RATE: load_standard_data,
        project_globals.DIARRHEA_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.DIARRHEA_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.DIARRHEA_DISABILITY_WEIGHT: load_standard_data,
        project_globals.DIARRHEA_RESTRICTIONS: load_metadata,

        project_globals.MEASLES_PREVALENCE: load_standard_data,
        project_globals.MEASLES_INCIDENCE_RATE: load_standard_data,
        project_globals.MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_DISABILITY_WEIGHT: load_standard_data,
        project_globals.MEASLES_RESTRICTIONS: load_metadata,

        project_globals.LRI_PREVALENCE: load_standard_data,
        project_globals.LRI_BIRTH_PREVALENCE: load_lri_birth_prevalence_from_meid,
        project_globals.LRI_INCIDENCE_RATE: load_standard_data,
        project_globals.LRI_REMISSION_RATE: load_standard_data,
        project_globals.LRI_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_DISABILITY_WEIGHT: load_standard_data,
        project_globals.LRI_RESTRICTIONS: load_metadata,

        project_globals.PEM_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_DISABILITY_WEIGHT: load_standard_data,
        project_globals.PEM_RESTRICTIONS: load_metadata,

        project_globals.WASTING_DISTRIBUTION: load_metadata,
        project_globals.WASTING_ALT_DISTRIBUTION: load_metadata,
        project_globals.WASTING_CATEGORIES: load_metadata,
        project_globals.WASTING_EXPOSURE_MEAN: load_standard_data,
        project_globals.WASTING_EXPOSURE_SD: load_standard_data,
        project_globals.WASTING_EXPOSURE_WEIGHTS: load_standard_data,
        project_globals.WASTING_RELATIVE_RISK: load_standard_data,
        project_globals.WASTING_PAF: load_standard_data,

        project_globals.STUNTING_DISTRIBUTION: load_metadata,
        project_globals.STUNTING_ALT_DISTRIBUTION: load_metadata,
        project_globals.STUNTING_CATEGORIES: load_metadata,
        project_globals.STUNTING_EXPOSURE_MEAN: load_standard_data,
        project_globals.STUNTING_EXPOSURE_SD: load_standard_data,
        project_globals.STUNTING_EXPOSURE_WEIGHTS: load_standard_data,
        project_globals.STUNTING_RELATIVE_RISK: load_standard_data,
        project_globals.STUNTING_PAF: load_standard_data,

        project_globals.LBWSG_DISTRIBUTION: load_metadata,
        project_globals.LBWSG_CATEGORIES: load_metadata,
        project_globals.LBWSG_EXPOSURE: load_lbwsg_exposure,
        project_globals.LBWSG_RELATIVE_RISK: load_lbwsg_relative_risk,
        project_globals.LBWSG_PAF: load_lbwsg_paf,

        project_globals.URI_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.OTITIS_MEDIA_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.PNEUMOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.H_INFLUENZAE_TYPE_B_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MENINGOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.OTHER_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.ENCEPHALITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_PRETERM_BIRTH_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_ENCEPHALOPATHY_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_SEPSIS_AND_OTHER_NEONATAL_INFECTIONS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.HEMOLYTIC_DISEASE_AND_OTHER_NEONATAL_JAUNDICE_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.OTHER_NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,

        project_globals.BIRTH_WEIGHT_BINS: load_bw_bin_data
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
    entity = get_entity(key)
    return interface.get_measure(entity, key.measure, location)


def load_metadata(key: str, location: str):
    key = EntityKey(key)
    entity = get_entity(key)
    metadata = entity[key.measure]
    if hasattr(metadata, 'to_dict'):
        metadata = metadata.to_dict()
    return metadata


def load_lbwsg_exposure(key: str, location: str):
    path = paths.lbwsg_data_path('exposure', location)
    data = pd.read_hdf(path)  # type: pd.DataFrame
    data['rei_id'] = risk_factors.low_birth_weight_and_short_gestation.gbd_id

    data = data.drop('modelable_entity_id', 'columns')
    data = data[data.parameter != 'cat124']  # LBWSG data has an extra residual category added by get_draws.
    data = utilities.filter_data_by_restrictions(data, risk_factors.low_birth_weight_and_short_gestation,
                                                 'outer', utility_data.get_age_group_ids())
    tmrel_cat = utility_data.get_tmrel_category(risk_factors.low_birth_weight_and_short_gestation)
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
    validation.validate_for_simulation(data, risk_factors.low_birth_weight_and_short_gestation,
                                       'exposure', location)
    data = utilities.split_interval(data, interval_column='age', split_column_prefix='age')
    data = utilities.split_interval(data, interval_column='year', split_column_prefix='year')
    return utilities.sort_hierarchical_data(data)


def load_lbwsg_relative_risk(key: str, location: str):
    path = paths.lbwsg_data_path('relative_risk', location)
    data = pd.read_hdf(path)  # type: pd.DataFrame
    data['rei_id'] = risk_factors.low_birth_weight_and_short_gestation.gbd_id
    data = utilities.convert_affected_entity(data, 'cause_id')
    # RRs for all causes are the same.
    data = data[data.affected_entity == 'diarrheal_diseases']
    data['affected_entity'] = 'all'
    # All lbwsg risk is about mortality.
    data.loc[:, 'affected_measure'] = 'excess_mortality_rate'
    data = data.filter(vi_globals.DEMOGRAPHIC_COLUMNS
                       + ['affected_entity', 'affected_measure', 'parameter']
                       + vi_globals.DRAW_COLUMNS)
    data = (
        data
            .groupby(['affected_entity', 'parameter'])
            .apply(utilities.normalize, fill_value=1)
            .reset_index(drop=True)
    )

    tmrel_cat = utility_data.get_tmrel_category(risk_factors.low_birth_weight_and_short_gestation)
    tmrel_mask = data.parameter == tmrel_cat
    data.loc[tmrel_mask, vi_globals.DRAW_COLUMNS] = (
        data
            .loc[tmrel_mask, vi_globals.DRAW_COLUMNS]
            .mask(np.isclose(data.loc[tmrel_mask, vi_globals.DRAW_COLUMNS], 1.0), 1.0)
    )

    data = utilities.reshape(data)
    data = utilities.scrub_gbd_conventions(data, location)
    validation.validate_for_simulation(data, risk_factors.low_birth_weight_and_short_gestation,
                                       'relative_risk', location)
    data = utilities.split_interval(data, interval_column='age', split_column_prefix='age')
    data = utilities.split_interval(data, interval_column='year', split_column_prefix='year')
    return utilities.sort_hierarchical_data(data)


def load_lbwsg_paf(key: str, location: str):
    path = paths.lbwsg_data_path('population_attributable_fraction', location)
    data = pd.read_hdf(path)  # type: pd.DataFrame
    data['rei_id'] = risk_factors.low_birth_weight_and_short_gestation.gbd_id
    data = data[data.metric_id == vi_globals.METRICS['Percent']]
    # All lbwsg risk is about mortality.
    data = data[data.measure_id.isin([vi_globals.MEASURES['YLLs']])]

    temp = []
    causes_map = {c.gbd_id: c for c in causes}
    # We filter paf age groups by cause level restrictions.
    for (c_id, measure), df in data.groupby(['cause_id', 'measure_id']):
        cause = causes_map[c_id]
        measure = 'yll' if measure == vi_globals.MEASURES['YLLs'] else 'yld'
        df = utilities.filter_data_by_restrictions(df, cause, measure, utility_data.get_age_group_ids())
        temp.append(df)
    data = pd.concat(temp, ignore_index=True)

    data = utilities.convert_affected_entity(data, 'cause_id')
    data.loc[data['measure_id'] == vi_globals.MEASURES['YLLs'], 'affected_measure'] = 'excess_mortality_rate'
    data = (data.groupby(['affected_entity', 'affected_measure'])
            .apply(utilities.normalize, fill_value=0)
            .reset_index(drop=True))
    data = data.filter(vi_globals.DEMOGRAPHIC_COLUMNS
                       + ['affected_entity', 'affected_measure']
                       + vi_globals.DRAW_COLUMNS)
    data = utilities.reshape(data)
    data = utilities.scrub_gbd_conventions(data, location)
    validation.validate_for_simulation(data, risk_factors.low_birth_weight_and_short_gestation,
                                       'population_attributable_fraction', location)
    data = utilities.split_interval(data, interval_column='age', split_column_prefix='age')
    data = utilities.split_interval(data, interval_column='year', split_column_prefix='year')
    return utilities.sort_hierarchical_data(data)


def load_lri_birth_prevalence_from_meid(_, location):
    """Ignore the first argument to fit in to the get_data model. """
    location_id = utility_data.get_location_id(location)
    data = get_draws('modelable_entity_id', project_globals.LRI_BIRTH_PREVALENCE_MEID,
                     source=project_globals.LRI_BIRTH_PREVALENCE_DRAW_SOURCE,
                     age_group_id=project_globals.LRI_BIRTH_PREVALENCE_AGE_ID,
                     measure_id=vi_globals.MEASURES['Prevalence'],
                     gbd_round_id=project_globals.LRI_BIRTH_PREVALENCE_GBD_ROUND,
                     location_id=location_id)
    data = data[data.measure_id == vi_globals.MEASURES['Prevalence']]
    data = utilities.normalize(data, fill_value=0)

    idx_columns = list(vi_globals.DEMOGRAPHIC_COLUMNS)
    idx_columns.remove('age_group_id')
    data = data.filter(idx_columns + vi_globals.DRAW_COLUMNS)

    data = utilities.reshape(data)
    data = utilities.scrub_gbd_conventions(data, location)
    data = utilities.split_interval(data, interval_column='year', split_column_prefix='year')
    return utilities.sort_hierarchical_data(data)

def load_bw_bin_data(_, location: str):
    return bw_risk.build_bw_rc_data(paths.birth_weight_bins_template_path(), location, paths.MODEL_SPEC_DIR)


def get_entity(key: str):
    # Map of entity types to their gbd mappings.
    type_map = {
        'cause': causes,
        'covariate': covariates,
        'risk_factor': risk_factors,
        'alternative_risk_factor': alternative_risk_factors
    }
    key = EntityKey(key)
    return type_map[key.type][key.name]
