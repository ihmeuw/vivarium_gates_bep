"""Loads, standardizes and validates input data for the simulation."""
from gbd_mapping import causes
import pandas as pd
from vivarium.framework.artifact import EntityKey
from vivarium_inputs import interface

from vivarium_gates_bep import globals as project_globals


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

        project_globals.MEASLES_PREVALENCE: load_standard_data,
        project_globals.MEASLES_INCIDENCE_RATE: load_standard_data,
        project_globals.MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.MEASLES_DISABILITY_WEIGHT: load_standard_data,

        project_globals.LRI_PREVALENCE: load_standard_data,
        project_globals.LRI_INCIDENCE_RATE: load_standard_data,
        project_globals.LRI_REMISSION_RATE: load_standard_data,
        project_globals.LRI_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.LRI_DISABILITY_WEIGHT: load_standard_data,

        project_globals.MENINGITIS_PREVALENCE: load_standard_data,
        project_globals.MENINGITIS_INCIDENCE_RATE: load_standard_data,
        project_globals.MENINGITIS_REMISSION_RATE: load_standard_data,
        project_globals.MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.MENINGITIS_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.MENINGITIS_DISABILITY_WEIGHT: load_meningitis_disability_weight,

        project_globals.PEM_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.PEM_DISABILITY_WEIGHT: load_standard_data,

        project_globals.NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_PREVALENCE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_BIRTH_PREVALENCE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_EXCESS_MORTALITY_RATE: load_standard_data,
        project_globals.NEONATAL_DISORDERS_DISABILITY_WEIGHT: load_standard_data,

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
