import itertools
from gbd_mapping import causes, risk_factors

CLUSTER_PROJECT = 'proj_cost_effect'
PROJECT_NAME = 'vivarium_gates_bep'

LBWSG_PATH = '/share/costeffectiveness/lbwsg/artifacts/'

LOCATIONS = [
    'India',
    'Mali',
    'Pakistan',
    'Tanzania',
]


# indicates measures that need to be pulled from specially created hdf files
LOCATIONS_WITH_DATA_PROBLEMS = [
    'India',
    'Mali',
    'Pakistan',
    'Tanzania',
]


def formatted_location(location):
    return location.replace(" ", "_").lower()


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
    causes.protein_energy_malnutrition.name
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

# other tracked events
LIVE_BIRTH = 'live_birth'
LOW_BIRTH_WEIGHT = 'low_birth_weight'
SHORT_GESTATION = 'short_gestation'
ALIVE_AT_6_MONTHS = 'alive_at_6_months'

# tracked metrics
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

SUSCEPTIBLE_DIARRHEA = 'susceptible_diarrhea'
ACTIVE_DIARRHEA = 'active_diarrhea'
DIARRHEA_STATES = [SUSCEPTIBLE_DIARRHEA, ACTIVE_DIARRHEA]
DIARRHEA_TRANSITIONS = [get_transition(SUSCEPTIBLE_DIARRHEA, ACTIVE_DIARRHEA),
                        get_transition(ACTIVE_DIARRHEA, SUSCEPTIBLE_DIARRHEA)]

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

STATES = (NEONATAL_SEPSIS_STATES + NEONATAL_ENCEPHALOPATHY_STATES + NEONATAL_JAUNDICE_STATES + DIARRHEA_STATES
          + LRI_STATES + MENINGITIS_STATES + MEASLES_STATES + PROTEIN_ENERGY_MALNUTRITION_STATES)

TRANSITIONS = (NEONATAL_SEPSIS_TRANSITIONS + NEONATAL_ENCEPHALOPATHY_TRANSITIONS + NEONATAL_JAUNDICE_TRANSITIONS
               + DIARRHEA_TRANSITIONS + LRI_TRANSITIONS + MENINGITIS_TRANSITIONS + MEASLES_TRANSITIONS
               + PROTEIN_ENERGY_MALNUTRITION_TRANSITIONS)

#################################
# Results columns and variables #
#################################

TOTAL_POP_COLUMN = 'total_population'
TOTAL_YLLS_COLUMN = 'years_of_life_lost'
TOTAL_YLDS_COLUMN = 'years_lived_with_disability'
TOTAL_PERSON_TIME_COLUMN = 'person_time'
RANDOM_SEED_COLUMN = 'random_seed'
INPUT_DRAW_COLUMN = 'input_draw'
SCENARIO_COLUMN = 'scenario'
COUNTRY_COLUMN = 'country'

STANDARD_COLUMNS = {
    'total_population': TOTAL_POP_COLUMN,
    'total_ylls': TOTAL_YLLS_COLUMN,
    'total_ylds': TOTAL_YLDS_COLUMN,
    'total_person_time': TOTAL_PERSON_TIME_COLUMN,
    'random_seed': RANDOM_SEED_COLUMN,
    'input_draw': INPUT_DRAW_COLUMN,
    'scenario': SCENARIO_COLUMN,
    'country': COUNTRY_COLUMN
}

PERSON_TIME_COLUMN_TEMPLATE = ('person_time_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                               'treatment_group_{TREATMENT_GROUP}')
PERSON_TIME_BY_STATE_COLUMN_TEMPLATE = ('person_time_{STATE}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                                        'treatment_group_{TREATMENT_GROUP}')
YLDS_COLUMN_TEMPLATE = ('ylds_due_to_{CAUSE_OF_DISABILITY}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                        'treatment_group_{TREATMENT_GROUP}')
YLLS_COLUMN_TEMPLATE = ('ylls_due_to_{CAUSE_OF_DEATH}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                        'treatment_group_{TREATMENT_GROUP}')
DALYS_COLUMN_TEMPLATE = ('dalys_due_to_{CAUSE_OF_DEATH}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                         'treatment_group_{TREATMENT_GROUP}')
DEATHS_COLUMN_TEMPLATE = ('death_due_to_{CAUSE_OF_DEATH}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                          'treatment_group_{TREATMENT_GROUP}')
COUNT_COLUMN_TEMPLATE = ('{COUNT_EVENT}_count_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                         'treatment_group_{TREATMENT_GROUP}')
MEAN_COLUMN_TEMPLATE = ('mean_{METRIC}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                        'treatment_group_{TREATMENT_GROUP}')
SD_COLUMN_TEMPLATE = ('standard_deviation_{METRIC}_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                      'treatment_group_{TREATMENT_GROUP}')
TRANSITION_COLUMN_TEMPLATE = ('{TRANSITION}_event_count_among_{MALNOURISHMENT_STATE}_in_age_group_{AGE_GROUP}_'
                              'treatment_group_{TREATMENT_GROUP}')

COLUMN_TEMPLATES = {
    'person_time': PERSON_TIME_COLUMN_TEMPLATE,
    'person_time_by_state': PERSON_TIME_BY_STATE_COLUMN_TEMPLATE,
    'ylds': YLDS_COLUMN_TEMPLATE,
    'ylls': YLLS_COLUMN_TEMPLATE,
    'dalys': DALYS_COLUMN_TEMPLATE,
    'death': DEATHS_COLUMN_TEMPLATE,
    'counts': COUNT_COLUMN_TEMPLATE,
    'means': MEAN_COLUMN_TEMPLATE,
    'standard_deviations': SD_COLUMN_TEMPLATE,
    'transitions': TRANSITION_COLUMN_TEMPLATE
}

TREATMENT_GROUPS = ['treated', 'untreated']
AGE_GROUPS = ['early_neonatal', 'late_neonatal', 'post_neonatal', '1_to_4']
CAUSES_OF_DISABILITY = list(CAUSE_MEASURES.keys()) + ['all_causes']
CAUSES_OF_DEATH = CAUSES_OF_DISABILITY + ['other_causes']
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
METRICS = [LAZ_AT_6_MONTHS, WLZ_AT_6_MONTHS, BIRTH_WEIGHT, GESTATIONAL_AGE]

TEMPLATE_FIELD_MAP = {
    'TREATMENT_GROUP': TREATMENT_GROUPS,
    'AGE_GROUP': AGE_GROUPS,
    'MALNOURISHMENT_STATE': MALNOURISHMENT_STATES,
    'CAUSE_OF_DISABILITY': CAUSES_OF_DISABILITY,
    'CAUSE_OF_DEATH': CAUSES_OF_DEATH,
    'COUNT_EVENT': COUNT_EVENTS + NEONATAL_CAUSES,
    'METRIC': METRICS,
    'STATE': STATES,
    'TRANSITION': TRANSITIONS
}

NEONATAL_SEPSIS_IR_MEID=1594


def result_columns(kind='all'):
    if kind not in COLUMN_TEMPLATES and kind != 'all':
        raise ValueError(f'Unknown result column type {kind}')
    columns = []
    if kind == 'all':
        for k in COLUMN_TEMPLATES:
            columns += result_columns(k)
        columns = list(STANDARD_COLUMNS.values()) + columns
    else:
        template = COLUMN_TEMPLATES[kind]
        filtered_field_map = {field: values
                              for field, values in TEMPLATE_FIELD_MAP.items() if f'{{{field}}}' in template}
        fields, value_groups = filtered_field_map.keys(), itertools.product(*filtered_field_map.values())
        for value_group in value_groups:
            columns.append(template.format(**{field: value for field, value in zip(fields, value_group)}))
    return columns
