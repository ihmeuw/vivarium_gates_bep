import itertools
import pandas as pd
from functools import partial
from pathlib import Path
from typing import Sequence, Mapping

from loguru import logger

from vivarium.framework.artifact import EntityKey, get_location_term, Artifact
from vivarium_inputs.data_artifact.loaders import loader

import vivarium_gates_bep.globals as bep_globals
from gbd_mapping import risk_factors


def safe_write(artifact: Artifact, keys: Sequence, getters: Mapping):
    for key in keys:
        if str(key) not in artifact:
            logger.info(f'>>> writing {key}.')
            data = getters[key]()
            artifact.write(key, data)
        else:
            logger.info(f'{key} found in artifact.')


def safe_write_by_draw(path, keys, getters):
    for key in keys:
        logger.info(f'looking for {key} draw-level data.')
        data = getters[key]()
        draws_written = []
        with pd.HDFStore(path, complevel=9, mode='a') as store:
            store.put(f'{key.path}/index', data.index.to_frame(index=False))
            data = data.reset_index(drop=True)
            for c in data.columns:
                draw_key = f'{key.path}/{c}'
                if draw_key not in store:
                    store.put(draw_key, data[c])
                    draws_written.append(c)
        if draws_written:
            logger.info(f">>> wrote data for draws [{' '.join(draws_written)}] under {key}.")
        else:
            logger.info(f"all draws found for {key}.")


def create_new_artifact(path: str, location: str) -> Artifact:
    logger.info(f"Creating artifact at {path}.")

    artifact = Artifact(path, filter_terms=[get_location_term(location)])
    key = EntityKey('metadata.locations')
    safe_write(artifact, [key], {key: lambda: [location]})
    return artifact


def write_demographic_data(artifact: Artifact, location: str):
    logger.info('Writing demographic data...')

    keys = [EntityKey('population.structure'),
            EntityKey('population.age_bins'),
            EntityKey('population.theoretical_minimum_risk_life_expectancy'),
            EntityKey('population.demographic_dimensions')]
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)


def write_covariate_data(artifact: Artifact, location: str):
    logger.info('Writing covariate data...')

    covariates = ['live_births_by_sex', 'antenatal_care_1_visit_coverage_proportion']
    measures = ['estimate']

    keys = [EntityKey(f'covariate.{c}.{m}') for c, m in itertools.product(covariates, measures)]
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)


def write_disease_data(artifact: Artifact, location: str):
    logger.info('Writing disease data...')
    for cause, measures in bep_globals.CAUSE_MEASURES.items():
        keys = [EntityKey(f'cause.{cause}.{m}') for m in measures]
        getters = {k: partial(loader, k, location, set()) for k in keys}
        safe_write(artifact, keys, getters)


def write_risk_data(artifact, location, risk):
    logger.info(f'Writing risk data for {risk}...')
    measures = ['exposure', 'population_attributable_fraction', 'relative_risk', 'distribution', 'categories']
    keys = [EntityKey(f'risk_factor.{risk}.{m}') for m in measures]
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)


def write_alternative_risk_data(artifact, location):
    logger.info('Writing risk data...')

    risks = ['child_wasting', 'child_underweight', 'child_stunting']
    measures = ['relative_risk', 'population_attributable_fraction', 'categories', 'distribution']
    alternative_measures = ['exposure', 'exposure_distribution_weights', 'exposure_standard_deviation', 'distribution']
    keys = [EntityKey(f'alternative_risk_factor.{r}.{m}') for r, m in itertools.product(risks, alternative_measures)]
    keys.extend([EntityKey(f'risk_factor.{r}.{m}') for r, m in itertools.product(risks, measures)])
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)


def write_lbwsg_data(artifact, location):
    logger.info('Writing low birth weight and short gestation data...')

    risk = 'low_birth_weight_and_short_gestation'
    measures = ['exposure', 'population_attributable_fraction', 'relative_risk']
    keys = [EntityKey(f'risk_factor.{risk}.{m}') for m in measures]

    # locations whose data was saved with an incompatible tables version
    if location in bep_globals.LOCATIONS_WITH_DATA_PROBLEMS:
        data_source = Path('/share/costeffectiveness/lbwsg/artifacts') / f"{location.replace(' ', '_')}.hdf"
        reversioned_artifact = Artifact(data_source)
        getters = {k: partial(reversioned_artifact.load, str(k)) for k in keys}
    else:
        getters = {k: partial(loader, k, location, set()) for k in keys}

    # these measures are not tables dependent
    metadata_measures = ['categories', 'distribution']
    metadata_keys = [EntityKey(f'risk_factor.{risk}.{m}') for m in metadata_measures]
    metadata_getters = {k: partial(loader, k, location, set()) for k in metadata_keys}
    keys.extend(metadata_keys)
    getters.update(metadata_getters)

    # relative risk is written by draw to save space
    rr_key = EntityKey(f'risk_factor.{risk}.relative_risk')
    keys.remove(rr_key)

    safe_write(artifact, keys, getters)
    safe_write_by_draw(artifact.path, [rr_key], {rr_key: getters.pop(rr_key)})


def write_iron_deficiency_data(artifact, location):
    logger.info(f'{location}: Writing data for iron deficiency')

    risk = 'iron_deficiency'
    measures = ['exposure', 'exposure_standard_deviation', 'distribution']
    keys = [EntityKey(f'risk_factor.{risk}.{m}') for m in measures]
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)

    categories_iron_deficiency = loader(EntityKey('cause.dietary_iron_deficiency.sequelae'), location, set())
    keys = [EntityKey(f'sequela.{cat}.disability_weight') for cat in categories_iron_deficiency]
    getters = {k: partial(loader, k, location, set()) for k in keys}
    safe_write(artifact, keys, getters)


def build_artifact(location: str, output_dir: str, erase: bool):
    artifact_path = Path(output_dir) / f'{location.replace(" ", "_").lower()}.hdf'
    if erase and artifact_path.is_file():
        artifact_path.unlink()
    artifact = create_new_artifact(artifact_path, location)
    write_demographic_data(artifact, location)
    write_covariate_data(artifact, location)
    write_disease_data(artifact, location)
    write_lbwsg_data(artifact, location)
    write_risk_data(artifact, location, risk_factors.vitamin_a_deficiency.name)
    write_alternative_risk_data(artifact, location)
    write_iron_deficiency_data(artifact, location)

    logger.info('!!! Done !!!')
