"""Main application functions for building artifacts.

.. admonition::

   Logging in this module should typically be done at the ``info`` level.
   Use your best judgement.

"""
from pathlib import Path

import click
from loguru import logger

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sanitize_location


def build_artifacts(location: str, output_dir: str, append: bool, verbose: int):
    """Main application function for building artifacts.

    Parameters
    ----------
    location
        The location to build the artifact for.  Must be one of the
        locations specified in the project globals or the string 'all'.
        If the latter, this application will build all artifacts in
        parallel.
    output_dir
        The path where the artifact files will be built.
    append
        Whether we should append to existing artifacts at the given output
        directory.  Has no effect if artifacts are not found.
    verbose
        How noisy the logger should be.

    """
    output_dir = Path(output_dir)

    if location in project_globals.LOCATIONS:
        path = Path(output_dir) / f'{sanitize_location(location)}.hdf'

        if path.exists() and not append:
            click.confirm(f"Existing artifact found for {location}. Do you want to delete and rebuild?",
                          abort=True)
            logger.info(f'Deleting artifact at {str(path)}.')
            path.unlink()

        build_single_location_artifact(path, location)

    elif location == 'all':
        # FIXME: could be more careful
        existing_artifacts = set([item.stem for item in output_dir.iterdir()
                                  if item.is_file() and item.suffix == '.hdf'])
        locations = set([sanitize_location(loc) for loc in project_globals.LOCATIONS])
        existing = locations.intersection(existing_artifacts)

        if existing and not append:
            click.confirm(f'Existing artifacts found for {existing}. Do you want to delete and rebuild?',
                          abort=True)
            for loc in existing:
                path = output_dir / f'{loc}.hdf'
                logger.info(f'Deleting artifact at {str(path)}.')
                path.unlink()

        build_all_artifacts(output_dir, verbose)

    else:
        raise ValueError(f'Location must be one of {project_globals.LOCATIONS} or the string "all". '
                         f'You specified {location}.')


def build_all_artifacts(output_dir, verbose):
    pass


def build_single_location_artifact(path, location, log_to_file=False):
    pass
