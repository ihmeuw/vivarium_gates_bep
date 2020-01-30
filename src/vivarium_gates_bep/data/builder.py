"""Modularized functions for building project data artifacts.

.. admonition::

   Logging in this module should be done at the ``debug`` level.

"""
from pathlib import Path

from loguru import logger
from vivarium.framework.artifact import Artifact, EntityKey, get_location_term

from vivarium_gates_bep import globals as project_globals


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

    key = EntityKey(project_globals.METADATA_LOCATIONS)
    if str(key) not in artifact:
        artifact.write(key, [location])

    return artifact
