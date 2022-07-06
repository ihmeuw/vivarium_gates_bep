from pathlib import Path

import vivarium_gates_bep
from vivarium_gates_bep import utilites, globals as project_globals

BASE_DIR = Path(vivarium_gates_bep.__file__).resolve().parent

ARTIFACT_ROOT = BASE_DIR / 'artifacts'
#MODEL_SPEC_DIR = (Path(__file__).parent / 'model_specifications').resolve()
MODEL_SPEC_DIR = BASE_DIR / 'model_specifications'
LBWSG_DATA_ROOT = ARTIFACT_ROOT / 'lbwsg'
BW_BINS_SPECFILE = 'bw_risk_corr_spec.in'

def lbwsg_data_path(measure: str, location: str):
    sanitized_location = utilites.sanitize_location(location)
    return LBWSG_DATA_ROOT / measure / f'{sanitized_location}.hdf'


def birth_weight_bins_template_path():
    return MODEL_SPEC_DIR / BW_BINS_SPECFILE
