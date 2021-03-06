"""Modularized functions for building project data artifacts.

.. admonition::

   Logging in this module should be done at the ``debug`` level.

"""
from pathlib import Path

from loguru import logger
import pandas as pd
from vivarium.framework.artifact import Artifact, get_location_term, EntityKey

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.data import loader


def open_artifact(output_path: Path, location: str) -> Artifact:
    """Creates or opens an artifact at the output path.

    Parameters
    ----------
    output_path
        Fully resolved path to the artifact file.
    location
        Proper GBD location name represented by the artifact.

    Returns
    -------
        A new artifact.

    """
    if not output_path.exists():
        logger.debug(f"Creating artifact at {str(output_path)}.")
    else:
        logger.debug(f"Opening artifact at {str(output_path)} for appending.")

    artifact = Artifact(output_path, filter_terms=[get_location_term(location)])

    key = project_globals.METADATA_LOCATIONS
    if key not in artifact:
        artifact.write(key, [location])

    return artifact


def load_and_write_data(artifact: Artifact, key: str, location: str):
    """Loads data and writes it to the artifact if not already present.

    Parameters
    ----------
    artifact
        The artifact to write to.
    key
        The entity key associated with the data to write.
    location
        The location associated with the data to load and the artifact to
        write to.

    """
    if key in artifact:
        logger.debug(f'Data for {key} already in artifact.  Skipping...')
    else:
        logger.debug(f'Loading data for {key} for location {location}.')
        data = loader.get_data(key, location)
        logger.debug(f'Writing data for {key} to artifact.')
        artifact.write(key, data)
    return artifact.load(key)


def write_data(artifact: Artifact, key: str, data: pd.DataFrame):
    """Writes data to the artifact if not already present.

    Parameters
    ----------
    artifact
        The artifact to write to.
    key
        The entity key associated with the data to write.
    data
        The data to write.

    """
    if key in artifact:
        logger.debug(f'Data for {key} already in artifact.  Skipping...')
    else:
        logger.debug(f'Writing data for {key} to artifact.')
        artifact.write(key, data)
    return artifact.load(key)


def write_data_by_draw(artifact: Artifact, key: str, data: pd.DataFrame):
    with pd.HDFStore(artifact.path, complevel=9, mode='a') as store:
        key = EntityKey(key)
        artifact._keys.append(key)
        store.put(f'{key.path}/index', data.index.to_frame(index=False))
        data = data.reset_index(drop=True)
        for c in data.columns:
            store.put(f'{key.path}/{c}', data[c])


def load_and_write_demographic_data(artifact: Artifact, location: str):
    keys = [
        project_globals.POPULATION_STRUCTURE,
        project_globals.POPULATION_AGE_BINS,
        project_globals.POPULATION_DEMOGRAPHY,
        project_globals.POPULATION_TMRLE,  # Theoretical life expectancy
        project_globals.ALL_CAUSE_CSMR,
        project_globals.COVARIATE_LIVE_BIRTHS_BY_SEX,
        project_globals.COVARIATE_ANC1_COVERAGE,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_diarrhea_data(artifact: Artifact, location: str):
    keys = [
        project_globals.DIARRHEA_PREVALENCE,
        project_globals.DIARRHEA_INCIDENCE_RATE,
        project_globals.DIARRHEA_REMISSION_RATE,
        project_globals.DIARRHEA_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.DIARRHEA_EXCESS_MORTALITY_RATE,
        project_globals.DIARRHEA_DISABILITY_WEIGHT,
        project_globals.DIARRHEA_RESTRICTIONS
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_measles_data(artifact: Artifact, location: str):
    keys = [
        project_globals.MEASLES_PREVALENCE,
        project_globals.MEASLES_INCIDENCE_RATE,
        project_globals.MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.MEASLES_EXCESS_MORTALITY_RATE,
        project_globals.MEASLES_DISABILITY_WEIGHT,
        project_globals.MEASLES_RESTRICTIONS
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_lri_data(artifact: Artifact, location: str):
    keys = [
        project_globals.LRI_PREVALENCE,
        project_globals.LRI_BIRTH_PREVALENCE,
        project_globals.LRI_INCIDENCE_RATE,
        project_globals.LRI_REMISSION_RATE,
        project_globals.LRI_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.LRI_EXCESS_MORTALITY_RATE,
        project_globals.LRI_DISABILITY_WEIGHT,
        project_globals.LRI_RESTRICTIONS,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_pem_data(artifact: Artifact, location: str):
    keys = [
        project_globals.PEM_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.PEM_EXCESS_MORTALITY_RATE,
        project_globals.PEM_DISABILITY_WEIGHT,
        project_globals.PEM_RESTRICTIONS,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_wasting_data(artifact: Artifact, location: str):
    keys = [
        project_globals.WASTING_DISTRIBUTION,
        project_globals.WASTING_ALT_DISTRIBUTION,
        project_globals.WASTING_CATEGORIES,
        project_globals.WASTING_EXPOSURE_MEAN,
        project_globals.WASTING_EXPOSURE_SD,
        project_globals.WASTING_EXPOSURE_WEIGHTS,
        project_globals.WASTING_RELATIVE_RISK,
        project_globals.WASTING_PAF,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_stunting_data(artifact: Artifact, location: str):
    keys = [
        project_globals.STUNTING_DISTRIBUTION,
        project_globals.STUNTING_ALT_DISTRIBUTION,
        project_globals.STUNTING_CATEGORIES,
        project_globals.STUNTING_EXPOSURE_MEAN,
        project_globals.STUNTING_EXPOSURE_SD,
        project_globals.STUNTING_EXPOSURE_WEIGHTS,
        project_globals.STUNTING_RELATIVE_RISK,
        project_globals.STUNTING_PAF,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_lbwsg_data(artifact: Artifact, location: str):
    keys = [
        project_globals.LBWSG_DISTRIBUTION,
        project_globals.LBWSG_CATEGORIES,
    ]
    draw_keys = [
        project_globals.LBWSG_EXPOSURE,
        project_globals.LBWSG_RELATIVE_RISK,
        project_globals.LBWSG_PAF
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)
    for key in draw_keys:
        if key in artifact:
            logger.debug(f'Data for {key} already in artifact.  Skipping...')
        else:
            logger.debug(f'Loading data for {key} for location {location}.')
            data = loader.get_data(key, location)
            logger.debug(f'Writing data for {key} to artifact.')
            write_data_by_draw(artifact, key, data)


def load_and_write_affected_unmodelled_lbwsg_csmr(artifact: Artifact, location: str):
    keys = [
        project_globals.URI_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.OTITIS_MEDIA_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.PNEUMOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.H_INFLUENZAE_TYPE_B_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.MENINGOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.OTHER_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.ENCEPHALITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.NEONATAL_PRETERM_BIRTH_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.NEONATAL_ENCEPHALOPATHY_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.NEONATAL_SEPSIS_AND_OTHER_NEONATAL_INFECTIONS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.HEMOLYTIC_DISEASE_AND_OTHER_NEONATAL_JAUNDICE_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.OTHER_NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)


def load_and_write_birth_weight_bin_data(artifact: Artifact, location: str):
    load_and_write_data(artifact, project_globals.BIRTH_WEIGHT_BINS, location)

