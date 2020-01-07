from pathlib import Path
from loguru import logger

import pandas as pd
import numpy as np

from gbd_mapping import causes
from vivarium import Artifact
from vivarium.framework.artifact import get_location_term
from vivarium.framework.artifact.hdf import EntityKey

from vivarium_inputs.data_artifact.loaders import loader
from vivarium_inputs.data_artifact.utilities import split_interval

import vivarium_gates_bep.globals as bep_globals


DIRECTORY_PERMS = 0o775
def build_artifact(path, location):
    # ensure the project artifact directory exists and has the correct permission
    Path(path).mkdir(exist_ok=True, parents=True)
    Path(path).chmod(DIRECTORY_PERMS)

    sanitized_location = location.lower().replace(" ", "_").replace("'", "-")
    artifact = create_new_artifact(path / f'{sanitized_location}.hdf', location)

    write_demographic_data(artifact, location)

    for disease in bep_globals.CAUSES_WITH_INCIDENCE:
        logger.info(f'{location}: Writing disease data for "{disease}"')
        write_disease_data(artifact, location, disease)

    for disease in bep_globals.CAUSES_NEONATAL:
        logger.info(f'{location}: Writing neonatal disease data for "{disease}"')
        write_neonatal_disease_data(artifact, location, disease)

    write_risk_data(artifact, location, bep_globals.RISK_FACTOR_VITAMIN_A)
    write_iron_deficiency_data(artifact, location)
    write_lbwsg_data(artifact, location)
    write_whz_haz_data(artifact, location)

    logger.info('!!! Done building artifact !!!')


def create_new_artifact(path: str, location: str) -> Artifact:
    if Path(path).is_file():
        Path(path).unlink()

    art = Artifact(path, filter_terms=[get_location_term(location)])
    art.write('metadata.locations', [location])
    return art


def get_load(location):
    return lambda key: loader(EntityKey(key), location, set())


def write_demographic_data(artifact, location):
    load = get_load(location)

    prefix = 'population.'
    measures = ["structure", "age_bins", "theoretical_minimum_risk_life_expectancy", "demographic_dimensions"]
    for m in measures:
        key = prefix + m
        write(artifact, key, load(key))

    key = 'cause.all_causes.cause_specific_mortality_rate'
    write(artifact, key, load(key))

    key = 'covariate.live_births_by_sex.estimate'
    write(artifact, key, load(key))


def compute_aggregate_prevalence_weighted_disability_weights(disease, loader):
    def check_mutual_exclusivity(subclass_prevalence, parent_prevalence):
        sc_sum = sum([df.mean().mean() for df in subclass_prevalence.values()])
        return np.isclose(sc_sum, parent_prevalence.mean().mean())

    parent_cause = [c for c in causes if c.name == disease][0]
    assert not parent_cause.most_detailed, 'Error: this is a most detailed cause'
    sub_causes = [s.name for s in parent_cause.sub_causes]

    # dictionary of dataframes with dw for each subcause
    df_dw_for_subcauses = {name : loader(f'cause.{name}.disability_weight') for name in sub_causes}

    # dictionary of dataframes with prevalence for each subcause
    df_prev_for_subcauses = {name : loader(f'cause.{name}.prevalence') for name in sub_causes}

    # parent prevalence
    df_prev_parent = loader(f'cause.{disease}.prevalence')
    assert check_mutual_exclusivity(df_prev_for_subcauses, df_prev_parent)

    # weight each subcause
    weights = {}
    for i in sub_causes:
        weights[i] = df_prev_for_subcauses[i] / df_prev_parent

    # adjust the disability weights
    weighted_dw = {}
    for key in df_dw_for_subcauses:
        weighted_dw[key] = df_dw_for_subcauses[key] * weights[key]

    # return the aggregate of the adjusted weights
    return sum(weighted_dw.values())


def write_common_disease_data(artifact, location, disease):
    load = get_load(location)

    # Metadata
    key = f'cause.{disease}.sequelae'
    sequelae = load(key)
    write(artifact, key, sequelae)

    key = f'cause.{disease}.restrictions'
    write(artifact, key, load(key))

    # Measures for Disease Model
    key = f'cause.{disease}.cause_specific_mortality_rate'
    write(artifact, key, load(key))

    # Measures for Disease States
    p, dw = load_prev_dw(sequelae, location)
    write(artifact, f'cause.{disease}.prevalence', p)
    write(artifact, f'cause.{disease}.disability_weight', dw)
    write(artifact, f'cause.{disease}.excess_mortality_rate', load(f'cause.{disease}.excess_mortality_rate'))


def write_no_sequela_disease_data(artifact, location, disease):
    load = get_load(location)

    key = f'cause.{disease}.restrictions'
    write(artifact, key, load(key))

    # Measures for Disease Model
    key = f'cause.{disease}.cause_specific_mortality_rate'
    write(artifact, key, load(key))

    # Measures for Disease States
    key = f'cause.{disease}.prevalence'
    write(artifact, key, load(key))
    write(artifact, f'cause.{disease}.disability_weight',
          compute_aggregate_prevalence_weighted_disability_weights(disease, load))
    key = f'cause.{disease}.excess_mortality_rate'
    write(artifact, key, load(key))

    load = get_load(location)
    key = f'cause.{disease}.incidence_rate'
    assert getattr(causes, disease).incidence_rate_exists
    write(artifact, key, load(key))
    key = f'cause.{disease}.remission_rate'
    write(artifact, key, load(key))


def write_disease_data(artifact, location, disease):
    if bep_globals.CAUSE_MENINGITIS == disease:
        write_no_sequela_disease_data(artifact, location, disease)
    else:
        write_common_disease_data(artifact, location, disease)

        # Measures for Transitions
        load = get_load(location)
        key = f'cause.{disease}.incidence_rate'
        assert getattr(causes, disease).incidence_rate_exists
        write(artifact, key, load(key))
        if disease != bep_globals.CAUSE_MEASLES:
            key = f'cause.{disease}.remission_rate'
            write(artifact, key, load(key))


def write_neonatal_disease_data(artifact, location, disease):
    write_common_disease_data(artifact, location, disease)

    # Measures for Transitions
    load = get_load(location)
    key = f'cause.{disease}.birth_prevalence'
    write(artifact, key, load(key))


def write_risk_data(artifact, location, risk):
    logger.info(f'{location}: Writing risk data for "{risk}"')
    load = get_load(location)

    risk_distribution_type = load(f'risk_factor.{risk}.distribution')
    write(artifact, f'risk_factor.{risk}.distribution', risk_distribution_type)

    categories = load(f'risk_factor.{risk}.categories')
    write(artifact, f'risk_factor.{risk}.categories', categories)

    for measure in ['exposure', 'population_attributable_fraction', 'relative_risk']:
        key = f'risk_factor.{risk}.{measure}'
        write(artifact, key, load(key))


def write_iron_deficiency_data(artifact, location):
    logger.info(f'{location}: Writing data for iron deficiency')
    load = get_load(location)

    for measure in ['exposure', 'exposure_standard_deviation']:
        key = f'risk_factor.iron_deficiency.{measure}'
        write(artifact, key, load(key))

    categories_iron_deficiency = load('cause.dietary_iron_deficiency.sequelae')
    for cat in categories_iron_deficiency:
        key = f'sequela.{cat}.disability_weight'
        write(artifact, key, load(key))


def get_lbwsg_for_loc(key, location, default_loader):
    mtype, category, measure = key.split('.')
    if location in bep_globals.LBWSG_MAPPER:
        sanitized_location =  location.replace(" ", "_").replace("'", "-")
        logger.info(f'Pulling lbwsg data from alternative location {bep_globals.LBWSG_PATH}/{sanitized_location}.hdf')
        art = Artifact(f'{bep_globals.LBWSG_PATH}/{sanitized_location}.hdf')
        return art.load(f'{mtype}.{category}.{measure}')
    else:
        logger.info(f'Pulling lbwsg data from GBD for "{location}"')
        return default_loader(key)


def write_lbwsg_data(artifact, location):
    logger.info(f'{location}: Writing low birthweight short gestation data.')
    load = get_load(location)
    for measure in ['exposure', 'population_attributable_fraction', 'relative_risk']:
        key = f'risk_factor.low_birth_weight_and_short_gestation.{measure}'
        data = get_lbwsg_for_loc(key, location, load)
        write(artifact, key, data)


def write_whz_haz_data(artifact, location):
    logger.info(f'{location}: Writing child wasting and stunting data.')
    load = get_load(location)

    for i in ['child_wasting', 'child_stunting']:
        key = f'alternative_risk_factor.{i}.distribution'
        write(artifact, key, load(key))
        write_risk_data(artifact, location, i)

    for measure in ['exposure', 'exposure_distribution_weights', 'exposure_standard_deviation']:
        key = f'alternative_risk_factor.child_wasting.{measure}'
        write(artifact, key, load(key))
        key = f'alternative_risk_factor.child_stunting.{measure}'
        write(artifact, key, load(key))



def load_prev_dw(sequela, location):
    load = get_load(location)
    prevalence = [load(f'sequela.{s}.prevalence') for s in sequela]
    disability_weight = [load(f'sequela.{s}.disability_weight') for s in sequela]
    total_prevalence = sum(prevalence)
    total_disability_weight = sum([p * dw for p, dw in zip(prevalence, disability_weight)]) / total_prevalence
    return total_prevalence, total_disability_weight


def write(artifact, key, data, skip_interval_processing=False):
    if skip_interval_processing:
        tmp = data
    else:
        tmp = data.copy(deep='all') if isinstance(data, pd.DataFrame) else data
        tmp = split_interval(tmp, interval_column='age', split_column_prefix='age')
        tmp = split_interval(tmp, interval_column='year', split_column_prefix='year')
    artifact.write(key, tmp)


