from gbd_mapping import causes, risk_factors


CLUSTER_PROJECT = 'proj_cost_effect'
PROJECT_NAME = 'vivarium_gates_bep'

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

CAUSE_MEASLES = causes.measles.name
CAUSE_DIARRHEAL = causes.diarrheal_diseases.name
CAUSE_LOWER_RESPIRATORY_INFECTIONS = causes.lower_respiratory_infections.name
CAUSE_MENINGITIS = causes.meningitis.name

CAUSE_NEONATAL_NEURAL_TUBE_DEFECTS = causes.neural_tube_defects.name
CAUSE_NEONATAL_ENCEPHALOPATHY = causes.neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma.name
CAUSE_NEONATAL_SEPSIS = causes.neonatal_sepsis_and_other_neonatal_infections.name
CAUSE_NEONATAL_JAUNDICE = causes.hemolytic_disease_and_other_neonatal_jaundice.name

RISK_FACTOR_VITAMIN_A = risk_factors.vitamin_a_deficiency.name


CAUSES_WITH_INCIDENCE = [
    CAUSE_MEASLES,
    CAUSE_DIARRHEAL,
    CAUSE_LOWER_RESPIRATORY_INFECTIONS,
    CAUSE_MENINGITIS,
]

CAUSES_NEONATAL = [
    CAUSE_NEONATAL_NEURAL_TUBE_DEFECTS,
    CAUSE_NEONATAL_ENCEPHALOPATHY,
    CAUSE_NEONATAL_SEPSIS,
    CAUSE_NEONATAL_JAUNDICE,
]


