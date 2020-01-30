"""Main application functions for building artifacts.

.. admonition::

   Logging in this module should typically be done at the ``info`` level.
   Use your best judgement.

"""
from pathlib import Path
import shutil
import sys
import time
from typing import Union

import click
from loguru import logger

from vivarium_gates_bep import globals as project_globals
from vivarium_gates_bep.utilites import sanitize_location
from vivarium_gates_bep.tools.app_logging import add_logging_sink


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


def build_all_artifacts(output_dir: Path, verbose: int):
    """Builds artifacts for all locations in parallel.

    Parameters
    ----------
    output_dir
        The directory where the artifacts will be built.
    verbose
        How noisy the logger should be.

    Note
    ----
        This function should not be called directly.  It is intended to be
        called by the :func:`build_artifacts` function located in the same
        module.


    """
    from vivarium_cluster_tools.psimulate.utilities import get_drmaa
    drmaa = get_drmaa()

    jobs = {}
    with drmaa.Session() as session:
        for location in project_globals.LOCATIONS:
            path = output_dir / f'{sanitize_location(location)}.hdf'

            job_template = session.createJobTemplate()
            job_template.remoteCommand = shutil.which("python")
            job_template.args = [__file__, str(path), f'"{location}"']
            job_template.nativeSpecification = (f'-V -b y -P {project_globals.CLUSTER_PROJECT} -q all.q '
                                                f'-l fmem=3G -l fthread=1 -l h_rt=3:00:00 -l archive=TRUE '
                                                f'-N {sanitize_location(location)}_artifact')
            jobs[location] = (session.runJob(job_template), drmaa.JobState.UNDETERMINED)
            logger.info(f'Submitted job {jobs[location][0]} to build artifact for {location}.')
            session.deleteJobTemplate(job_template)

        decodestatus = {drmaa.JobState.UNDETERMINED: 'undetermined',
                        drmaa.JobState.QUEUED_ACTIVE: 'queued_active',
                        drmaa.JobState.SYSTEM_ON_HOLD: 'system_hold',
                        drmaa.JobState.USER_ON_HOLD: 'user_hold',
                        drmaa.JobState.USER_SYSTEM_ON_HOLD: 'user_system_hold',
                        drmaa.JobState.RUNNING: 'running',
                        drmaa.JobState.SYSTEM_SUSPENDED: 'system_suspended',
                        drmaa.JobState.USER_SUSPENDED: 'user_suspended',
                        drmaa.JobState.DONE: 'finished',
                        drmaa.JobState.FAILED: 'failed'}

        if verbose:
            logger.info('Entering monitoring loop.')
            logger.info('-------------------------')
            logger.info('')

            while any([job[1] not in [drmaa.JobState.DONE, drmaa.JobState.FAILED] for job in jobs.values()]):
                for location, (job_id, status) in jobs.items():
                    jobs[location] = (job_id, session.jobStatus(job_id))
                    logger.info(f'{location:<35}: {decodestatus[jobs[location][1]]:>15}')
                logger.info('')
                time.sleep(10)
                logger.info('Checking status again')
                logger.info('---------------------')
                logger.info('')

    logger.info('**Done**')


def build_single_location_artifact(path: Union[str, Path], location: str, log_to_file: bool = False):
    """Builds an artifact for a single location.

    Parameters
    ----------
    path
        The full path to the artifact to build.
    location
        The location to build the artifact for.  Must be one of the locations
        specified in the project globals.
    log_to_file
        Whether we should write the application logs to a file.

    Note
    ----
        This function should not be called directly.  It is intended to be
        called by the :func:`build_artifacts` function located in the same
        module.

    """
    location = location.strip('"')
    path = Path(path)
    if log_to_file:
        log_file = path.parent / 'logs' / f'{sanitize_location(location)}.log'
        if log_file.exists():
            log_file.unlink()
        add_logging_sink(log_file, verbose=2)

    # Local import to avoid data dependencies
    from vivarium_gates_bep.data import builder

    # TODO: call all the artifact building functions.

    logger.info('**DONE**')


if __name__ == "__main__":
    artifact_path = sys.argv[1]
    artifact_location = sys.argv[2]
    build_single_location_artifact(artifact_path, artifact_location, log_to_file=True)