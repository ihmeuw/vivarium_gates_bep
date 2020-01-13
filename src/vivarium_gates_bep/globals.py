from gbd_mapping import causes, risk_factors


CLUSTER_PROJECT = 'proj_cost_effect'
PROJECT_NAME = 'vivarium_gates_bep'

LBWSG_PATH = '/share/costeffectiveness/lbwsg/artifacts/'

LOCATIONS = [
    'Burkina Faso',
    'Ethiopia',
    'India',
    'Malawi',
    'Mali',
    'Nepal',
    'Pakistan',
    'Tanzania',
]


# indicates measures that need to be pulled from specially created hdf files
LOCATIONS_WITH_DATA_PROBLEMS = [
    'India',
    'Malawi',
    'Mali',
    'Pakistan',
    'Tanzania',
]


DEFAULT_CAUSE_LIST = ['cause_specific_mortality_rate', 'excess_mortality_rate', 'disability_weight',
         'incidence_rate', 'prevalence', 'remission_rate', 'restrictions']
NEONATAL_CAUSE_LIST = ['cause_specific_mortality_rate', 'excess_mortality_rate', 'disability_weight',
         'birth_prevalence', 'prevalence', 'restrictions']

CAUSE_MEASURES = {
    'all_causes': ['cause_specific_mortality_rate'],
    'diarrheal_diseases': DEFAULT_CAUSE_LIST,
    'lower_respiratory_infections': DEFAULT_CAUSE_LIST,
    'meningitis': DEFAULT_CAUSE_LIST,
    'measles': [c for c in DEFAULT_CAUSE_LIST if c not in ['remission_rate']],
    'neonatal_sepsis_and_other_neonatal_infections': NEONATAL_CAUSE_LIST,
    'neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma': NEONATAL_CAUSE_LIST,
    'hemolytic_disease_and_other_neonatal_jaundice': NEONATAL_CAUSE_LIST,
    'neural_tube_defects': NEONATAL_CAUSE_LIST,
    #'neonatal_preterm_birth':[c for c in NEONATAL_CAUSE_LIST if c not in ['birth_prevalence', 'prevalence']]
}


