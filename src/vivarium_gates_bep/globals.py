import itertools
from typing import NamedTuple

####################
# Project metadata #
####################

PROJECT_NAME = 'vivarium_gates_bep'
CLUSTER_PROJECT = 'proj_cost_effect'
CLUSTER_QUEUE = 'all.q'

MAKE_ARTIFACT_MEM = '3G'
MAKE_ARTIFACT_CPU = '1'
MAKE_ARTIFACT_RUNTIME = '4:00:00'

LOCATIONS = [
    'India',
    'Mali',
    'Pakistan',
    'Tanzania',
]


###################
# Model Constants #
###################
# This is a collection of constants used in data generation or as
# invariant model parameters.  Sources for these parameters can be found
# in the concept model document.
# TODO: Include concept model document in repository.

def twenty_percent_of_mean_variance(mean):
    ninety_five_percent_spread = .2 * mean
    std_dev = ninety_five_percent_spread / (2 * 1.96)
    return std_dev ** 2


def confidence_interval_std(upper, lower):
    ninety_five_percent_spread = (upper - lower)
    return ninety_five_percent_spread / (2 * 1.96)


def confidence_interval_variance(upper, lower):
    return confidence_interval_std(upper, lower) ** 2


MALNOURISHED_MOTHERS_PROPORTION_MEAN = {
    'India': .168,
    'Mali': .103,
    'Pakistan': .107,
    'Tanzania': .095
}
MALNOURISHED_MOTHERS_PROPORTION_VARIANCE = {location: twenty_percent_of_mean_variance(mean)
                                            for location, mean in MALNOURISHED_MOTHERS_PROPORTION_MEAN.items()}
MALNOURISHED_MOTHERS_EFFECT_RR_MEAN = 2
MALNOURISHED_MOTHERS_EFFECT_RR_LOWER_BOUND = 1.5
MALNOURISHED_MOTHERS_EFFECT_RR_SHAPE = 2
MALNOURISHED_MOTHERS_EFFECT_RR_PARAMETERS = {
    'mean': MALNOURISHED_MOTHERS_EFFECT_RR_MEAN,
    'lower_bound': MALNOURISHED_MOTHERS_EFFECT_RR_LOWER_BOUND,
    'shape': MALNOURISHED_MOTHERS_EFFECT_RR_SHAPE,
}


IFA_COVERAGE_AMONG_ANC_MEAN = {
    'India': .387,
    'Mali': .280,
    'Pakistan': .294,
    'Tanzania': .214
}
IFA_COVERAGE_AMONG_ANC_VARIANCE = {location: twenty_percent_of_mean_variance(mean)
                                   for location, mean in IFA_COVERAGE_AMONG_ANC_MEAN.items()}

IFA_BIRTH_WEIGHT_SHIFT_SIZE_MEAN = 57.73
IFA_BIRTH_WEIGHT_SHIFT_SIZE_LOWER = 7.66
IFA_BIRTH_WEIGHT_SHIFT_SIZE_UPPER = 107.79
IFA_BIRTH_WEIGHT_SHIFT_SIZE_LOWER_BOUND = 0
IFA_BIRTH_WEIGHT_SHIFT_SIZE_UPPER_BOUND = 120
IFA_BIRTH_WEIGHT_SHIFT_SIZE_VARIANCE = confidence_interval_variance(IFA_BIRTH_WEIGHT_SHIFT_SIZE_UPPER,
                                                                    IFA_BIRTH_WEIGHT_SHIFT_SIZE_LOWER)
IFA_BIRTH_WEIGHT_SHIFT_SIZE_PARAMETERS = {
    'mean': IFA_BIRTH_WEIGHT_SHIFT_SIZE_MEAN,
    'variance': IFA_BIRTH_WEIGHT_SHIFT_SIZE_VARIANCE,
    'lower_bound': IFA_BIRTH_WEIGHT_SHIFT_SIZE_LOWER_BOUND,
    'upper_bound': IFA_BIRTH_WEIGHT_SHIFT_SIZE_UPPER_BOUND
}

MMN_BIRTH_WEIGHT_SHIFT_SIZE_MEAN = 45.16
MMN_BIRTH_WEIGHT_SHIFT_SIZE_LOWER = 32.31
MMN_BIRTH_WEIGHT_SHIFT_SIZE_UPPER = 58.02
MMN_BIRTH_WEIGHT_SHIFT_SIZE_LOWER_BOUND = 0
MMN_BIRTH_WEIGHT_SHIFT_SIZE_UPPER_BOUND = 75
MMN_BIRTH_WEIGHT_SHIFT_SIZE_VARIANCE = confidence_interval_variance(MMN_BIRTH_WEIGHT_SHIFT_SIZE_UPPER,
                                                                    MMN_BIRTH_WEIGHT_SHIFT_SIZE_LOWER)
MMN_BIRTH_WEIGHT_SHIFT_SIZE_PARAMETERS = {
    'mean': MMN_BIRTH_WEIGHT_SHIFT_SIZE_MEAN,
    'variance': MMN_BIRTH_WEIGHT_SHIFT_SIZE_VARIANCE,
    'lower_bound': MMN_BIRTH_WEIGHT_SHIFT_SIZE_LOWER_BOUND,
    'upper_bound': MMN_BIRTH_WEIGHT_SHIFT_SIZE_UPPER_BOUND
}

# Two different sets of effect sizes, denoted by these strings
EFFECT_CURRENT_EVIDENCE = 'CurrentEvidence'
EFFECT_HOPES_AND_DREAMS = 'HopesAndDreams'

BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_MEAN = 75
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER = 65
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER = 85
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER_BOUND = 50
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER_BOUND = 100
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_VARIANCE = confidence_interval_variance(
    BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER,BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER)

# BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_MEAN = 40.96
# BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER = 4.66
# BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER = 77.26
# # TODO - what are bounds?
# BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER_BOUND = 0
# BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER_BOUND = 80
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_MEAN = 15.93
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER = -20.83
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER = 52.69
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER_BOUND = -23
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER_BOUND = 54
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_VARIANCE = confidence_interval_variance(
    BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER, BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER)

BEP_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_PARAMETERS = {
    EFFECT_CURRENT_EVIDENCE: {
        'mean': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_MEAN,
        'variance': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_VARIANCE,
        'lower_bound': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER_BOUND,
        'upper_bound': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER_BOUND
    },
    EFFECT_HOPES_AND_DREAMS: {
        'mean': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_MEAN,
        'variance': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_VARIANCE,
        'lower_bound': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_LOWER_BOUND,
        'upper_bound': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_NORMAL_UPPER_BOUND
    }
}

CRUDE_BW_SHIFT = 142.93
CRUDE_BW_SHIFT_UPPER = 232.68
CRUDE_BW_SHIFT_LOWER = 53.18
CRUDE_BW_SHIFT_SD = (CRUDE_BW_SHIFT_UPPER - CRUDE_BW_SHIFT_LOWER) / (2 * 1.98)


BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_MEAN = 100
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER = 90
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER = 110
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER_BOUND = 75
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER_BOUND = 125
BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_VARIANCE = confidence_interval_variance(
    BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER, BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER)


BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_MEAN = 66.96
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER = 13.3
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER = 120.78
# TODO - what should bounds be?
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER_BOUND = 5
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER_BOUND = 140
BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_VARIANCE = confidence_interval_variance(
    BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER, BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER)

BEP_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_PARAMETERS = {
    EFFECT_CURRENT_EVIDENCE: {
        'mean': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_MEAN,
        'variance': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_VARIANCE,
        'lower_bound': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER_BOUND,
        'upper_bound': BEP_CE_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER_BOUND
    },
    EFFECT_HOPES_AND_DREAMS: {
        'mean': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_MEAN,
        'variance': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_VARIANCE,
        'lower_bound': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_LOWER_BOUND,
        'upper_bound': BEP_HD_BIRTH_WEIGHT_SHIFT_SIZE_MALNOURISHED_UPPER_BOUND
    }
}

BEP_HD_CGF_SHIFT_SIZE_MEAN = 0.3
BEP_HD_CGF_SHIFT_SIZE_LOWER = 0.2
BEP_HD_CGF_SHIFT_SIZE_UPPER = 0.4
BEP_HD_CGF_SHIFT_SIZE_LOWER_BOUND = 0.
BEP_HD_CGF_SHIFT_SIZE_UPPER_BOUND = 1.
BEP_HD_CGF_SHIFT_SIZE_VARIANCE = confidence_interval_variance(BEP_HD_CGF_SHIFT_SIZE_UPPER,
                                                           BEP_HD_CGF_SHIFT_SIZE_LOWER)
BEP_CE_CGF_SHIFT_SIZE = 0.0

BEP_CGF_SHIFT_SIZE_PARAMETERS = {
    'mean': BEP_HD_CGF_SHIFT_SIZE_MEAN,
    'variance': BEP_HD_CGF_SHIFT_SIZE_VARIANCE,
    'lower_bound': BEP_HD_CGF_SHIFT_SIZE_LOWER_BOUND,
    'upper_bound': BEP_HD_CGF_SHIFT_SIZE_UPPER_BOUND
}


#############
# Data Keys #
#############

METADATA_LOCATIONS = 'metadata.locations'

POPULATION_STRUCTURE = 'population.structure'
POPULATION_AGE_BINS = 'population.age_bins'
POPULATION_DEMOGRAPHY = 'population.demographic_dimensions'
POPULATION_TMRLE = 'population.theoretical_minimum_risk_life_expectancy'

ALL_CAUSE_CSMR = 'cause.all_causes.cause_specific_mortality_rate'

COVARIATE_ANC1_COVERAGE = 'covariate.antenatal_care_1_visit_coverage_proportion.estimate'
COVARIATE_LIVE_BIRTHS_BY_SEX = 'covariate.live_births_by_sex.estimate'

DIARRHEA_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.diarrheal_diseases.cause_specific_mortality_rate'
DIARRHEA_PREVALENCE = 'cause.diarrheal_diseases.prevalence'
DIARRHEA_INCIDENCE_RATE = 'cause.diarrheal_diseases.incidence_rate'
DIARRHEA_REMISSION_RATE = 'cause.diarrheal_diseases.remission_rate'
DIARRHEA_EXCESS_MORTALITY_RATE = 'cause.diarrheal_diseases.excess_mortality_rate'
DIARRHEA_DISABILITY_WEIGHT = 'cause.diarrheal_diseases.disability_weight'
DIARRHEA_RESTRICTIONS = 'cause.diarrheal_diseases.restrictions'

MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.measles.cause_specific_mortality_rate'
MEASLES_PREVALENCE = 'cause.measles.prevalence'
MEASLES_INCIDENCE_RATE = 'cause.measles.incidence_rate'
MEASLES_EXCESS_MORTALITY_RATE = 'cause.measles.excess_mortality_rate'
MEASLES_DISABILITY_WEIGHT = 'cause.measles.disability_weight'
MEASLES_RESTRICTIONS = 'cause.measles.restrictions'

LRI_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.lower_respiratory_infections.cause_specific_mortality_rate'
LRI_BIRTH_PREVALENCE = 'cause.lower_respiratory_infections.birth_prevalence'
LRI_BIRTH_PREVALENCE_MEID = 1258
LRI_BIRTH_PREVALENCE_DRAW_SOURCE = 'epi'
LRI_BIRTH_PREVALENCE_AGE_ID = 164
LRI_BIRTH_PREVALENCE_GBD_ROUND = 5
LRI_PREVALENCE = 'cause.lower_respiratory_infections.prevalence'
LRI_INCIDENCE_RATE = 'cause.lower_respiratory_infections.incidence_rate'
LRI_REMISSION_RATE = 'cause.lower_respiratory_infections.remission_rate'
LRI_EXCESS_MORTALITY_RATE = 'cause.lower_respiratory_infections.excess_mortality_rate'
LRI_DISABILITY_WEIGHT = 'cause.lower_respiratory_infections.disability_weight'
LRI_RESTRICTIONS = 'cause.lower_respiratory_infections.restrictions'

PEM_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.protein_energy_malnutrition.cause_specific_mortality_rate'
PEM_EXCESS_MORTALITY_RATE = 'cause.protein_energy_malnutrition.excess_mortality_rate'
PEM_DISABILITY_WEIGHT = 'cause.protein_energy_malnutrition.disability_weight'
PEM_RESTRICTIONS = 'cause.protein_energy_malnutrition.restrictions'


WASTING_DISTRIBUTION = 'risk_factor.child_wasting.distribution'
WASTING_ALT_DISTRIBUTION = 'alternative_risk_factor.child_wasting.distribution'
WASTING_CATEGORIES = 'risk_factor.child_wasting.categories'
WASTING_EXPOSURE_MEAN = 'alternative_risk_factor.child_wasting.exposure'
WASTING_EXPOSURE_SD = 'alternative_risk_factor.child_wasting.exposure_standard_deviation'
WASTING_EXPOSURE_WEIGHTS = 'alternative_risk_factor.child_wasting.exposure_distribution_weights'
WASTING_RELATIVE_RISK = 'risk_factor.child_wasting.relative_risk'
WASTING_PAF = 'risk_factor.child_wasting.population_attributable_fraction'

STUNTING_DISTRIBUTION = 'risk_factor.child_stunting.distribution'
STUNTING_ALT_DISTRIBUTION = 'alternative_risk_factor.child_stunting.distribution'
STUNTING_CATEGORIES = 'risk_factor.child_stunting.categories'
STUNTING_EXPOSURE_MEAN = 'alternative_risk_factor.child_stunting.exposure'
STUNTING_EXPOSURE_SD = 'alternative_risk_factor.child_stunting.exposure_standard_deviation'
STUNTING_EXPOSURE_WEIGHTS = 'alternative_risk_factor.child_stunting.exposure_distribution_weights'
STUNTING_RELATIVE_RISK = 'risk_factor.child_stunting.relative_risk'
STUNTING_PAF = 'risk_factor.child_stunting.population_attributable_fraction'

LBWSG_DISTRIBUTION = 'risk_factor.low_birth_weight_and_short_gestation.distribution'
LBWSG_CATEGORIES = 'risk_factor.low_birth_weight_and_short_gestation.categories'
LBWSG_EXPOSURE = 'risk_factor.low_birth_weight_and_short_gestation.exposure'
LBWSG_RELATIVE_RISK = 'risk_factor.low_birth_weight_and_short_gestation.relative_risk'
LBWSG_PAF = 'risk_factor.low_birth_weight_and_short_gestation.population_attributable_fraction'

BIRTH_WEIGHT_BINS = 'birth_weight.bins'


# Cause specific mortality rates for causes affected by LBWSG but not included as a Disease Model
URI_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.upper_respiratory_infections.cause_specific_mortality_rate'
OTITIS_MEDIA_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.otitis_media.cause_specific_mortality_rate'
PNEUMOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.pneumococcal_meningitis.cause_specific_mortality_rate'
H_INFLUENZAE_TYPE_B_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.h_influenzae_type_b_meningitis.cause_specific_mortality_rate'
MENINGOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.meningococcal_meningitis.cause_specific_mortality_rate'
OTHER_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.other_meningitis.cause_specific_mortality_rate'
ENCEPHALITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.encephalitis.cause_specific_mortality_rate'
NEONATAL_PRETERM_BIRTH_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.neonatal_preterm_birth.cause_specific_mortality_rate'
NEONATAL_ENCEPHALOPATHY_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma.cause_specific_mortality_rate'
NEONATAL_SEPSIS_AND_OTHER_NEONATAL_INFECTIONS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.neonatal_sepsis_and_other_neonatal_infections.cause_specific_mortality_rate'
HEMOLYTIC_DISEASE_AND_OTHER_NEONATAL_JAUNDICE_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.hemolytic_disease_and_other_neonatal_jaundice.cause_specific_mortality_rate'
OTHER_NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.other_neonatal_disorders.cause_specific_mortality_rate'


UNMODELLED_LBWSG_AFFECTED_CAUSES = [
    URI_CAUSE_SPECIFIC_MORTALITY_RATE,
    OTITIS_MEDIA_CAUSE_SPECIFIC_MORTALITY_RATE,
    PNEUMOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
    H_INFLUENZAE_TYPE_B_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
    MENINGOCOCCAL_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
    OTHER_MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
    ENCEPHALITIS_CAUSE_SPECIFIC_MORTALITY_RATE,
    NEONATAL_PRETERM_BIRTH_CAUSE_SPECIFIC_MORTALITY_RATE,
    NEONATAL_ENCEPHALOPATHY_CAUSE_SPECIFIC_MORTALITY_RATE,
    NEONATAL_SEPSIS_AND_OTHER_NEONATAL_INFECTIONS_CAUSE_SPECIFIC_MORTALITY_RATE,
    HEMOLYTIC_DISEASE_AND_OTHER_NEONATAL_JAUNDICE_CAUSE_SPECIFIC_MORTALITY_RATE,
    OTHER_NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE,
]


###########################
# Disease Model Constants #
###########################

DIARRHEA_MODEL_NAME = 'diarrheal_diseases'
DIARRHEA_SUSCEPTIBLE_STATE_NAME = f'susceptible_to_{DIARRHEA_MODEL_NAME}'
DIARRHEA_WITH_CONDITION_STATE_NAME = DIARRHEA_MODEL_NAME
DIARRHEA_MODEL_STATES = (DIARRHEA_SUSCEPTIBLE_STATE_NAME, DIARRHEA_WITH_CONDITION_STATE_NAME)
DIARRHEA_MODEL_TRANSITIONS = (
    f'{DIARRHEA_SUSCEPTIBLE_STATE_NAME}_TO_{DIARRHEA_WITH_CONDITION_STATE_NAME}',
    f'{DIARRHEA_WITH_CONDITION_STATE_NAME}_TO_{DIARRHEA_SUSCEPTIBLE_STATE_NAME}',
)

MEASLES_MODEL_NAME = 'measles'
MEASLES_SUSCEPTIBLE_STATE_NAME = f'susceptible_to_{MEASLES_MODEL_NAME}'
MEASLES_WITH_CONDITION_STATE_NAME = MEASLES_MODEL_NAME
MEASLES_RECOVERED_STATE_NAME = f'recovered_from_{MEASLES_MODEL_NAME}'
MEASLES_MODEL_STATES = (MEASLES_SUSCEPTIBLE_STATE_NAME, MEASLES_WITH_CONDITION_STATE_NAME, MEASLES_RECOVERED_STATE_NAME)
MEASLES_MODEL_TRANSITIONS = (
    f'{MEASLES_SUSCEPTIBLE_STATE_NAME}_TO_{MEASLES_WITH_CONDITION_STATE_NAME}',
    f'{MEASLES_WITH_CONDITION_STATE_NAME}_TO_{MEASLES_RECOVERED_STATE_NAME}',
)

LRI_MODEL_NAME = 'lower_respiratory_infections'
LRI_SUSCEPTIBLE_STATE_NAME = f'susceptible_to_{LRI_MODEL_NAME}'
LRI_WITH_CONDITION_STATE_NAME = LRI_MODEL_NAME
LRI_MODEL_STATES = (LRI_SUSCEPTIBLE_STATE_NAME, LRI_WITH_CONDITION_STATE_NAME)
LRI_MODEL_TRANSITIONS = (
    f'{LRI_SUSCEPTIBLE_STATE_NAME}_TO_{LRI_WITH_CONDITION_STATE_NAME}',
    f'{LRI_WITH_CONDITION_STATE_NAME}_TO_{LRI_SUSCEPTIBLE_STATE_NAME}',
)

PEM_MODEL_NAME = 'protein_energy_malnutrition'
PEM_SUSCEPTIBLE_STATE_NAME = f'susceptible_to_{PEM_MODEL_NAME}'
PEM_WITH_CONDITION_STATE_NAME = PEM_MODEL_NAME
PEM_MODEL_STATES = (PEM_SUSCEPTIBLE_STATE_NAME, PEM_WITH_CONDITION_STATE_NAME)
PEM_MODEL_TRANSITIONS = (
    f'{PEM_SUSCEPTIBLE_STATE_NAME}_TO_{PEM_WITH_CONDITION_STATE_NAME}',
    f'{PEM_WITH_CONDITION_STATE_NAME}_TO_{PEM_SUSCEPTIBLE_STATE_NAME}',
)

DISEASE_MODELS = (DIARRHEA_MODEL_NAME, MEASLES_MODEL_NAME, LRI_MODEL_NAME, PEM_MODEL_NAME)
DISEASE_MODEL_MAP = {
    DIARRHEA_MODEL_NAME: {
        'states': DIARRHEA_MODEL_STATES,
        'transitions': DIARRHEA_MODEL_TRANSITIONS,
    },
    MEASLES_MODEL_NAME: {
        'states': MEASLES_MODEL_STATES,
        'transitions': MEASLES_MODEL_TRANSITIONS,
    },
    LRI_MODEL_NAME: {
        'states': LRI_MODEL_STATES,
        'transitions': LRI_MODEL_TRANSITIONS,
    },
    PEM_MODEL_NAME: {
        'states': PEM_MODEL_STATES,
        'transitions': PEM_MODEL_TRANSITIONS,
    },
}

########################
# Risk Model Constants #
########################

LBWSG_MODEL_NAME = 'low_birth_weight_and_short_gestation'
BIRTH_WEIGHT = 'birth_weight'
BIRTH_WEIGHT_PROPENSITY = 'birth_weight_propensity'
GESTATION_TIME = 'gestation_time'
LBWSG_COLUMNS = [BIRTH_WEIGHT, GESTATION_TIME]
LBWSG_COLUMNS_CORR = [BIRTH_WEIGHT, GESTATION_TIME, BIRTH_WEIGHT_PROPENSITY]
UNDERWEIGHT = 2500  # grams
MAX_BIRTH_WEIGHT = 4500  # grams
PRETERM = 37  # weeks
MAX_GESTATIONAL_TIME = 42  # weeks


class __LBWSG_MISSING_CATEGORY(NamedTuple):
    CAT: str = 'cat212'
    NAME: str = 'Birth prevalence - [37, 38) wks, [1000, 1500) g'
    EXPOSURE: float = 0.


LBWSG_MISSING_CATEGORY = __LBWSG_MISSING_CATEGORY()


WASTING_MODEL_NAME = 'child_wasting'
STUNTING_MODEL_NAME = 'child_stunting'


MATERNAL_MALNUTRITION_MODEL_NAME = 'maternal_malnutrition'
MOTHER_NUTRITION_STATUS_COLUMN = 'mother_malnourished'
MOTHER_NUTRITION_NORMAL = 'normal'
MOTHER_NUTRITION_MALNOURISHED = 'malnourished'
MOTHER_NUTRITION_CATEGORIES = (MOTHER_NUTRITION_NORMAL, MOTHER_NUTRITION_MALNOURISHED)


#############################
# Treatment Model Constants #
#############################

class __SCENARIOS(NamedTuple):
    BASELINE: str = 'baseline'
    IFA: str = 'ifa_scale_up'
    MMN: str = 'mmn_scale_up'
    BEP_CE: str = 'bep_ce_scale_up'
    BEP_HD: str = 'bep_hd_scale_up'
    BEP_CE_TARGETED: str = 'bep_ce_targeted_scale_up'
    BEP_HD_TARGETED: str = 'bep_hd_targeted_scale_up'


SCENARIOS = __SCENARIOS()


class __TREATMENTS(NamedTuple):
    NONE: str = 'none'
    IFA: str = 'ifa'
    MMN: str = 'mmn'
    BEP: str = 'bep'


TREATMENTS = __TREATMENTS()

TREATMENT_MODEL_NAME = 'maternal_supplementation'
BASELINE_COLUMN = 'baseline_maternal_supplementation_type'
SCENARIO_COLUMN = 'scenario_maternal_supplementation_type'

#################################
# Results columns and variables #
#################################

# Standard columns from core components.
TOTAL_POPULATION_COLUMN = 'total_population'
TOTAL_YLDS_COLUMN = 'years_lived_with_disability'
TOTAL_YLLS_COLUMN = 'years_of_life_lost'
SINGLE_COLUMNS = (TOTAL_POPULATION_COLUMN, TOTAL_YLLS_COLUMN, TOTAL_YLDS_COLUMN)

# Columns from parallel runs
INPUT_DRAW_COLUMN = 'input_draw'
RANDOM_SEED_COLUMN = 'random_seed'
OUTPUT_SCENARIO_COLUMN = 'maternal_supplementation.scenario'

PSIMULATE_COLUMNS = (INPUT_DRAW_COLUMN, RANDOM_SEED_COLUMN, OUTPUT_SCENARIO_COLUMN)

# Data columns for randomly sampled data
MALNOURISHED_MOTHERS_PROPORTION_COLUMN = 'maternal_malnourishment_proportion'

STATES = tuple(state for model in DISEASE_MODELS for state in DISEASE_MODEL_MAP[model]['states'])
THROWAWAY_COLUMNS = ([f'{state}_event_count' for state in STATES]
                     + [f'{state}_prevalent_cases_at_sim_end' for state in STATES if 'susceptible' not in state and 'recovered' not in state]
                     + [MALNOURISHED_MOTHERS_PROPORTION_COLUMN])


TOTAL_POPULATION_COLUMN_TEMPLATE = 'total_population_{POP_STATE}'
TOTAL_POPULATION_COLUMN_STRATIFIED_TEMPLATE = 'total_population_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
PERSON_TIME_COLUMN_TEMPLATE = 'person_time_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
DEATH_COLUMN_TEMPLATE = 'death_due_to_{CAUSE_OF_DEATH}_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
YLLS_COLUMN_TEMPLATE = 'ylls_due_to_{CAUSE_OF_DEATH}_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
YLDS_COLUMN_TEMPLATE = 'ylds_due_to_{CAUSE_OF_DISABILITY}_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
STATE_PERSON_TIME_COLUMN_TEMPLATE = '{STATE}_person_time_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
TRANSITION_COUNT_COLUMN_TEMPLATE = '{TRANSITION}_event_count_in_age_group_{AGE_GROUP}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
Z_SCORE_COLUMNS = '{CGF_RISK}_z_score_{STATS_MEASURE}_at_six_months_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
CATEGORY_COUNT_COLUMNS = '{CGF_RISK}_{RISK_CATEGORY}_exposed_at_six_months_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
BIRTH_WEIGHT_COLUMNS = 'birth_weight_{BIRTH_WEIGHT_MEASURE}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'
GESTATIONAL_AGE_COLUMNS = 'gestational_age_{GESTATIONAL_AGE_MEASURE}_mother_{MALNOURISHMENT_CATEGORY}_treatment_{TREATMENT_CATEGORY}'


COLUMN_TEMPLATES = {
    'population': TOTAL_POPULATION_COLUMN_TEMPLATE,
    'population_stratified': TOTAL_POPULATION_COLUMN_STRATIFIED_TEMPLATE,
    'person_time': PERSON_TIME_COLUMN_TEMPLATE,
    'deaths': DEATH_COLUMN_TEMPLATE,
    'ylls': YLLS_COLUMN_TEMPLATE,
    'ylds': YLDS_COLUMN_TEMPLATE,
    'state_person_time': STATE_PERSON_TIME_COLUMN_TEMPLATE,
    'transition_count': TRANSITION_COUNT_COLUMN_TEMPLATE,
    'z_scores': Z_SCORE_COLUMNS,
    'category_counts': CATEGORY_COUNT_COLUMNS,
    'birth_weight': BIRTH_WEIGHT_COLUMNS,
    'gestational_age': GESTATIONAL_AGE_COLUMNS,
}

NON_COUNT_TEMPLATES = [
    'z_scores',
    'birth_weight',
    'gestational_age',
]


POP_STATES = ('living', 'dead', 'tracked', 'untracked')
YEARS = ('2020', '2021', '2022')
SEXES = ('male', 'female')
AGE_GROUPS = ('early_neonatal', 'late_neonatal', '1mo_to_6mo', '6mo_to_1', '1_to_4')
CAUSES_OF_DEATH = (
    'other_causes',
    DIARRHEA_WITH_CONDITION_STATE_NAME,
    MEASLES_WITH_CONDITION_STATE_NAME,
    LRI_WITH_CONDITION_STATE_NAME,
    PEM_WITH_CONDITION_STATE_NAME,
)
CAUSES_OF_DISABILITY = (
    DIARRHEA_WITH_CONDITION_STATE_NAME,
    MEASLES_WITH_CONDITION_STATE_NAME,
    LRI_WITH_CONDITION_STATE_NAME,
    PEM_WITH_CONDITION_STATE_NAME,
)
STATES = tuple(state for model in DISEASE_MODELS for state in DISEASE_MODEL_MAP[model]['states'])
TRANSITIONS = tuple(transition.lower() for model in DISEASE_MODELS for transition in DISEASE_MODEL_MAP[model]['transitions'])
CGF_RISKS = ('wasting', 'stunting')
STATS_MEASURES = ('mean', 'sd')
RISK_CATEGORIES = ('cat1', 'cat2', 'cat3', 'cat4')
BIRTH_WEIGHT_MEASURES = STATS_MEASURES + ('proportion_below_2500g',)
GESTATIONAL_AGE_MEASURES = STATS_MEASURES + ('proportion_below_37w',)
MALNOURISHMENT_CATEGORIES = ('malnourished', 'normal')
TREATMENT_CATEGORIES = tuple(TREATMENTS)


TEMPLATE_FIELD_MAP = {
    'POP_STATE': POP_STATES,
    'AGE_GROUP': AGE_GROUPS,
    'CAUSE_OF_DEATH': CAUSES_OF_DEATH,
    'CAUSE_OF_DISABILITY': CAUSES_OF_DISABILITY,
    'STATE': STATES,
    'TRANSITION': TRANSITIONS,
    'CGF_RISK': CGF_RISKS,
    'STATS_MEASURE': STATS_MEASURES,
    'RISK_CATEGORY': RISK_CATEGORIES,
    'BIRTH_WEIGHT_MEASURE': BIRTH_WEIGHT_MEASURES,
    'GESTATIONAL_AGE_MEASURE': GESTATIONAL_AGE_MEASURES,
    'MALNOURISHMENT_CATEGORY': MALNOURISHMENT_CATEGORIES,
    'TREATMENT_CATEGORY': TREATMENT_CATEGORIES,
}


def RESULT_COLUMNS(kind='all'):
    if kind not in COLUMN_TEMPLATES and kind != 'all':
        raise ValueError(f'Unknown result column type {kind}')
    columns = []
    if kind == 'all':
        for k in COLUMN_TEMPLATES:
            columns += RESULT_COLUMNS(k)
        columns = list(SINGLE_COLUMNS) + columns
    else:
        template = COLUMN_TEMPLATES[kind]
        filtered_field_map = {field: values
                              for field, values in TEMPLATE_FIELD_MAP.items() if f'{{{field}}}' in template}
        fields, value_groups = filtered_field_map.keys(), itertools.product(*filtered_field_map.values())
        for value_group in value_groups:
            columns.append(template.format(**{field: value for field, value in zip(fields, value_group)}))
    return columns
