"""Modularized functions for building project data artifacts.

.. admonition::

   Logging in this module should be done at the ``debug`` level.

"""
from pathlib import Path

from gbd_mapping import causes
from loguru import logger
import pandas as pd
from vivarium.framework.artifact import Artifact, get_location_term

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


def load_and_write_demographic_data(artifact: Artifact, location: str):
    keys = [
        project_globals.POPULATION_STRUCTURE,
        project_globals.POPULATION_AGE_BINS,
        project_globals.POPULATION_DEMOGRAPHY,
        project_globals.POPULATION_TMRLE,  # Theoretical life expectancy
        project_globals.ALL_CAUSE_CSMR,
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
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)

    write_data(artifact, project_globals.DIARRHEA_RESTRICTIONS, causes.diarrheal_diseases.restrictions.to_dict())


def load_and_write_measles_data(artifact: Artifact, location: str):
    keys = [
        project_globals.MEASLES_PREVALENCE,
        project_globals.MEASLES_INCIDENCE_RATE,
        project_globals.MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.MEASLES_EXCESS_MORTALITY_RATE,
        project_globals.MEASLES_DISABILITY_WEIGHT,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)

    write_data(artifact, project_globals.MEASLES_RESTRICTIONS, causes.measles.restrictions.to_dict())


def load_and_write_lri_data(artifact: Artifact, location: str):
    keys = [
        project_globals.LRI_PREVALENCE,
        project_globals.LRI_INCIDENCE_RATE,
        project_globals.LRI_REMISSION_RATE,
        project_globals.LRI_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.LRI_EXCESS_MORTALITY_RATE,
        project_globals.LRI_DISABILITY_WEIGHT,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)

    write_data(artifact, project_globals.LRI_RESTRICTIONS, causes.lower_respiratory_infections.restrictions.to_dict())


def load_and_write_meningitis_data(artifact: Artifact, location: str):
    keys = [
        project_globals.MENINGITIS_PREVALENCE,
        project_globals.MENINGITIS_INCIDENCE_RATE,
        project_globals.MENINGITIS_REMISSION_RATE,
        project_globals.MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
        project_globals.MENINGITIS_EXCESS_MORTALITY_RATE,
        project_globals.MENINGITIS_DISABILITY_WEIGHT,
    ]

    for key in keys:
        load_and_write_data(artifact, key, location)

    write_data(artifact, project_globals.MENINGITIS_RESTRICTIONS, causes.meningitis.restrictions.to_dict())
