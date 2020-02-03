import itertools
from gbd_mapping import causes, risk_factors

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


#############
# Data Keys #
#############

METADATA_LOCATIONS = 'metadata.locations'

POPULATION_STRUCTURE = 'population.structure'
POPULATION_AGE_BINS = 'population.age_bins'
POPULATION_DEMOGRAPHY = 'population.demographic_dimensions'
POPULATION_TMRLE = 'population.theoretical_minimum_risk_life_expectancy'

ALL_CAUSE_CSMR = 'cause.all_causes.cause_specific_mortality_rate'

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
LRI_PREVALENCE = 'cause.lower_respiratory_infections.prevalence'
LRI_INCIDENCE_RATE = 'cause.lower_respiratory_infections.incidence_rate'
LRI_REMISSION_RATE = 'cause.lower_respiratory_infections.remission_rate'
LRI_EXCESS_MORTALITY_RATE = 'cause.lower_respiratory_infections.excess_mortality_rate'
LRI_DISABILITY_WEIGHT = 'cause.lower_respiratory_infections.disability_weight'
LRI_RESTRICTIONS = 'cause.lower_respiratory_infections.restrictions'

MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.meningitis.cause_specific_mortality_rate'
MENINGITIS_PREVALENCE = 'cause.meningitis.prevalence'
MENINGITIS_INCIDENCE_RATE = 'cause.meningitis.incidence_rate'
MENINGITIS_REMISSION_RATE = 'cause.meningitis.remission_rate'
MENINGITIS_EXCESS_MORTALITY_RATE = 'cause.meningitis.excess_mortality_rate'
MENINGITIS_DISABILITY_WEIGHT = 'cause.meningitis.disability_weight'
MENINGITIS_RESTRICTIONS = 'cause.meningitis.restrictions'

PEM_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.protein_energy_malnutrition.cause_specific_mortality_rate'
PEM_EXCESS_MORTALITY_RATE = 'cause.protein_energy_malnutrition.excess_mortality_rate'
PEM_DISABILITY_WEIGHT = 'cause.protein_energy_malnutrition.disability_weight'
PEM_RESTRICTIONS = 'cause.protein_energy_malnutrition.restrictions'

NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE = 'cause.neonatal_disorders.cause_specific_mortality_rate'
NEONATAL_DISORDERS_PREVALENCE = 'cause.neonatal_disorders.prevalence'
NEONATAL_DISORDERS_BIRTH_PREVALENCE = 'cause.neonatal_disorders.birth_prevalence'
NEONATAL_DISORDERS_EXCESS_MORTALITY_RATE = 'cause.neonatal_disorders.excess_mortality_rate'
NEONATAL_DISORDERS_DISABILITY_WEIGHT = 'cause.neonatal_disorders.disability_weight'
NEONATAL_DISORDERS_RESTRICTIONS = 'cause.neonatal_disorders.restrictions'


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


###########################
# Disease Model variables #
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

DISEASE_MODELS = (DIARRHEA_MODEL_NAME, MEASLES_MODEL_NAME, LRI_MODEL_NAME)
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
    }
}

#################################
# Results columns and variables #
#################################

TOTAL_POPULATION_COLUMN = 'total_population'
TOTAL_YLDS_COLUMN = 'years_lived_with_disability'
TOTAL_YLLS_COLUMN = 'years_of_life_lost'

STANDARD_COLUMNS = {
    'total_population': TOTAL_POPULATION_COLUMN,
    'total_ylls': TOTAL_YLLS_COLUMN,
    'total_ylds': TOTAL_YLDS_COLUMN,
}

TOTAL_POPULATION_COLUMN_TEMPLATE = 'total_population_{POP_STATE}'
PERSON_TIME_COLUMN_TEMPLATE = 'person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
DEATH_COLUMN_TEMPLATE = 'death_due_to_{CAUSE_OF_DEATH}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
YLLS_COLUMN_TEMPLATE = 'ylls_due_to_{CAUSE_OF_DEATH}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
YLDS_COLUMN_TEMPLATE = 'ylds_due_to_{CAUSE_OF_DISABILITY}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
STATE_PERSON_TIME_COLUMN_TEMPLATE = '{STATE}_person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
TRANSITION_COUNT_COLUMN_TEMPLATE = '{TRANSITION}_event_count_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'


COLUMN_TEMPLATES = {
    'population': TOTAL_POPULATION_COLUMN_TEMPLATE,
    'person_time': PERSON_TIME_COLUMN_TEMPLATE,
    'deaths': DEATH_COLUMN_TEMPLATE,
    'ylls': YLLS_COLUMN_TEMPLATE,
    'ylds': YLDS_COLUMN_TEMPLATE,
    'state_person_time': STATE_PERSON_TIME_COLUMN_TEMPLATE,
    'transition_count': TRANSITION_COUNT_COLUMN_TEMPLATE,
}


POP_STATES = ['living', 'dead', 'tracked', 'untracked']
YEARS = ['2020', '2021', '2022']
SEXES = ['male', 'female']
AGE_GROUPS = ['early_neonatal', 'late_neonatal', 'post_neonatal', '1_to_4']
CAUSES_OF_DEATH = ['other_causes', DIARRHEA_MODEL_NAME, MEASLES_MODEL_NAME, LRI_MODEL_NAME]
CAUSES_OF_DISABILITY = [DIARRHEA_MODEL_NAME, MEASLES_MODEL_NAME, LRI_MODEL_NAME]
STATES = [state for model in DISEASE_MODELS for state in DISEASE_MODEL_MAP[model]['states']]
TRANSITIONS = [transition for model in DISEASE_MODELS for transition in DISEASE_MODEL_MAP[model]['transitions']]


TEMPLATE_FIELD_MAP = {
    'POP_STATE': POP_STATES,
    'YEAR': YEARS,
    'SEX': SEXES,
    'AGE_GROUP': AGE_GROUPS,
    'CAUSE_OF_DEATH': CAUSES_OF_DEATH,
}


def RESULT_COLUMNS(kind='all'):
    if kind not in COLUMN_TEMPLATES and kind != 'all':
        raise ValueError(f'Unknown result column type {kind}')
    columns = []
    if kind == 'all':
        for k in COLUMN_TEMPLATES:
            columns += RESULT_COLUMNS(k)
        columns = list(STANDARD_COLUMNS.values()) + columns
    else:
        template = COLUMN_TEMPLATES[kind]
        filtered_field_map = {field: values
                              for field, values in TEMPLATE_FIELD_MAP.items() if f'{{{field}}}' in template}
        fields, value_groups = filtered_field_map.keys(), itertools.product(*filtered_field_map.values())
        for value_group in value_groups:
            columns.append(template.format(**{field: value for field, value in zip(fields, value_group)}))
    return columns


#########
# Other #
#########


DEFAULT_CAUSE_LIST = ['cause_specific_mortality_rate', 'excess_mortality_rate', 'disability_weight',
         'incidence_rate', 'prevalence', 'remission_rate', 'restrictions']
NEONATAL_CAUSE_LIST = ['cause_specific_mortality_rate', 'excess_mortality_rate', 'disability_weight',
         'birth_prevalence', 'prevalence', 'restrictions']

NEONATAL_CAUSES = [
    causes.neonatal_sepsis_and_other_neonatal_infections.name,
    causes.neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma.name,
    causes.hemolytic_disease_and_other_neonatal_jaundice.name
]

OTHER_CAUSES = [
    causes.diarrheal_diseases.name,
    causes.lower_respiratory_infections.name,
    causes.meningitis.name,
    causes.measles.name,
    # TODO uncomment when disease weight is calculated
    # causes.protein_energy_malnutrition.name
]

CAUSE_MEASURES = dict(
    {causes.all_causes.name: ['cause_specific_mortality_rate'],
     causes.measles.name: [c for c in DEFAULT_CAUSE_LIST if c != 'remission_rate']},
    **{neonatal_cause: NEONATAL_CAUSE_LIST for neonatal_cause in NEONATAL_CAUSES},
    **{other_cause: DEFAULT_CAUSE_LIST for other_cause in OTHER_CAUSES if other_cause != causes.measles.name}
)

# Tracked risk factors
# TODO do we use risk_factors.child_and_maternal_malnutrition?
MALNOURISHMENT_EXPOSED = 'exposed_to_maternal_malnourishment'
MALNOURISHMENT_UNEXPOSED = 'unexposed_to_maternal_malnourishment'
MALNOURISHMENT_CATEGORIES = ['cat1', 'cat2']
MALNOURISHMENT_STATES = [MALNOURISHMENT_EXPOSED, MALNOURISHMENT_UNEXPOSED]
MALNOURISHMENT_MAP = {MALNOURISHMENT_CATEGORIES[i]: state for i, state in enumerate(MALNOURISHMENT_STATES)}

TREATMENT_GROUPS = ['treated', 'untreated']

STRATIFICATION_GROUPS = list(itertools.product(MALNOURISHMENT_CATEGORIES, AGE_GROUPS, TREATMENT_GROUPS))

# other tracked events
LIVE_BIRTH = 'live_birth'
LOW_BIRTH_WEIGHT = 'low_birth_weight'
SHORT_GESTATION = 'short_gestation'
ALIVE_AT_6_MONTHS = 'alive_at_6_months'

# tracked metrics
PERSON_TIME = 'person_time'
DEATH = 'death'
YLLS = 'ylls'
YLDS = 'ylds'
DALYS = 'dalys'
LAZ_AT_6_MONTHS = 'laz_at_6_months'
WLZ_AT_6_MONTHS = 'wlz_at_6_months'
BIRTH_WEIGHT = 'birth_weight'
GESTATIONAL_AGE = 'gestational_age'


def get_transition(state_a, state_b):
    return f'{state_a}_to_{state_b}'


# States and Transitions
SUSCEPTIBLE_NEONATAL_SEPSIS = 'susceptible_neonatal_sepsis'
ACTIVE_NEONATAL_SEPSIS = 'active_neonatal_sepsis'
NEONATAL_SEPSIS_STATES = [SUSCEPTIBLE_NEONATAL_SEPSIS, ACTIVE_NEONATAL_SEPSIS]
NEONATAL_SEPSIS_TRANSITIONS = [get_transition(SUSCEPTIBLE_NEONATAL_SEPSIS, ACTIVE_NEONATAL_SEPSIS),
                               get_transition(ACTIVE_NEONATAL_SEPSIS, SUSCEPTIBLE_NEONATAL_SEPSIS)]

SUSCEPTIBLE_NEONATAL_ENCEPHALOPATHY = 'susceptible_neonatal_encephalopathy'
ACTIVE_NEONATAL_ENCEPHALOPATHY = 'active_neonatal_encephalopathy'
NEONATAL_ENCEPHALOPATHY_STATES = [SUSCEPTIBLE_NEONATAL_ENCEPHALOPATHY, ACTIVE_NEONATAL_ENCEPHALOPATHY]
NEONATAL_ENCEPHALOPATHY_TRANSITIONS = [
    get_transition(SUSCEPTIBLE_NEONATAL_ENCEPHALOPATHY, ACTIVE_NEONATAL_ENCEPHALOPATHY),
    get_transition(ACTIVE_NEONATAL_ENCEPHALOPATHY, SUSCEPTIBLE_NEONATAL_ENCEPHALOPATHY)
]

SUSCEPTIBLE_NEONATAL_JAUNDICE = 'susceptible_neonatal_jaundice'
ACTIVE_NEONATAL_JAUNDICE = 'active_neonatal_jaundice'
NEONATAL_JAUNDICE_STATES = [SUSCEPTIBLE_NEONATAL_JAUNDICE, ACTIVE_NEONATAL_JAUNDICE]
NEONATAL_JAUNDICE_TRANSITIONS = [get_transition(SUSCEPTIBLE_NEONATAL_JAUNDICE, ACTIVE_NEONATAL_JAUNDICE),
                                 get_transition(ACTIVE_NEONATAL_JAUNDICE, SUSCEPTIBLE_NEONATAL_JAUNDICE)]


SUSCEPTIBLE_LRI = 'susceptible_lower_respiratory_infection'
ACTIVE_LRI = 'active_lower_respiratory_infection'
LRI_STATES = [SUSCEPTIBLE_LRI, ACTIVE_LRI]
LRI_TRANSITIONS = [get_transition(SUSCEPTIBLE_LRI, ACTIVE_LRI), get_transition(ACTIVE_LRI, SUSCEPTIBLE_LRI)]

SUSCEPTIBLE_MENINGITIS = 'susceptible_meningitis'
ACTIVE_MENINGITIS = 'active_meningitis'
MENINGITIS_STATES = [SUSCEPTIBLE_MENINGITIS, ACTIVE_MENINGITIS]
MENINGITIS_TRANSITIONS = [get_transition(SUSCEPTIBLE_MENINGITIS, ACTIVE_MENINGITIS),
                          get_transition(ACTIVE_MENINGITIS, SUSCEPTIBLE_MENINGITIS)]

SUSCEPTIBLE_PROTEIN_ENERGY_MALNUTRITION = 'susceptible_protein_energy_malnutrition'
ACTIVE_PROTEIN_ENERGY_MALNUTRITION = 'active_protein_energy_malnutrition'
PROTEIN_ENERGY_MALNUTRITION_STATES = [SUSCEPTIBLE_PROTEIN_ENERGY_MALNUTRITION, ACTIVE_PROTEIN_ENERGY_MALNUTRITION]
PROTEIN_ENERGY_MALNUTRITION_TRANSITIONS = [
    get_transition(SUSCEPTIBLE_PROTEIN_ENERGY_MALNUTRITION, ACTIVE_PROTEIN_ENERGY_MALNUTRITION),
    get_transition(ACTIVE_PROTEIN_ENERGY_MALNUTRITION, SUSCEPTIBLE_PROTEIN_ENERGY_MALNUTRITION)
]

SUSCEPTIBLE_MEASLES = 'susceptible_measles'
ACTIVE_MEASLES = 'active_measles'
EXPOSED_MEASLES = 'exposed_measles'
MEASLES_STATES = [SUSCEPTIBLE_MEASLES, ACTIVE_MEASLES, EXPOSED_MEASLES]
MEASLES_TRANSITIONS = [get_transition(SUSCEPTIBLE_MEASLES, ACTIVE_MEASLES),
                       get_transition(ACTIVE_MEASLES, EXPOSED_MEASLES)]

#################################
# Results columns and variables #
#################################
MOCKED_COLUMN_VALUE = -99.0

RANDOM_SEED_COLUMN = 'random_seed'
INPUT_DRAW_COLUMN = 'input_draw'
SCENARIO_COLUMN = 'scenario'
COUNTRY_COLUMN = 'country'



METRIC_COLUMN_TEMPLATE = ('{METRIC}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                          'treatment_group_{TREATMENT_GROUP}')

DALYS_COLUMN_TEMPLATE = ('dalys_due_to_{CAUSE_OF_DEATH}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                         'treatment_group_{TREATMENT_GROUP}')

COUNT_COLUMN_TEMPLATE = ('{COUNT_EVENT}_count_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                         'treatment_group_{TREATMENT_GROUP}')


COUNT_EVENTS = [
    LIVE_BIRTH,
    LOW_BIRTH_WEIGHT,
    SHORT_GESTATION,
    f'{risk_factors.child_wasting.name}_cat1',
    f'{risk_factors.child_wasting.name}_cat2',
    f'{risk_factors.child_wasting.name}_cat3',
    f'{risk_factors.child_stunting.name}_cat1',
    f'{risk_factors.child_stunting.name}_cat2',
    f'{risk_factors.child_stunting.name}_cat3',
    ALIVE_AT_6_MONTHS
]

METRICS = [PERSON_TIME, DEATH, YLLS, YLDS, DALYS] + [
    f'{stat}_{metric}'
    for metric in [LAZ_AT_6_MONTHS, WLZ_AT_6_MONTHS, BIRTH_WEIGHT, GESTATIONAL_AGE]
    for stat in ['mean', 'sd']
]


NEONATAL_SEPSIS_IR_MEID=1594


