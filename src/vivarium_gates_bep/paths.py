from pathlib import Path

from vivarium_gates_bep import utilites, globals as project_globals


ARTIFACT_ROOT = Path(f"/share/costeffectiveness/artifacts/{project_globals.PROJECT_NAME}/")
MODEL_SPEC_DIR = (Path(__file__).parent / 'model_specifications').resolve()
LBWSG_DATA_ROOT = Path(f'/share/costeffectiveness/lbwsg_new/data')
BW_BINS_SPECFILE = 'bw_risk_corr_spec.in'

def lbwsg_data_path(measure: str, location: str):
    sanitized_location = utilites.sanitize_location(location)
    return LBWSG_DATA_ROOT / measure / f'{sanitized_location}.hdf'


def birth_weight_bins_template_path():
    return MODEL_SPEC_DIR / BW_BINS_SPECFILE
