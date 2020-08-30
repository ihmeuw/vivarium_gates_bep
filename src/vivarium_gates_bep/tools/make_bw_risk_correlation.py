"""Application functions for producing specification files from which we derive birth weight risk correlation."""
import numpy as np
import pandas as pd

from pathlib import Path

from vivarium import InteractiveContext
from vivarium_gates_bep.tools.make_specs import build_model_specifications
from vivarium_gates_bep.utilites import sanitize_location


LARGER_THAN_LARGEST_BABY_ON_RECORD = 25 * 454


def create_bw_rc_data(spec_file: str):
    sim = InteractiveContext(spec_file)
    df = pd.DataFrame()
    df['birth_weights'] = sim.get_population().birth_weight

    # rank birth weights
    df = df.sort_values(by=['birth_weights']).reset_index(drop=True)

    # create upper and lower bounds, fill starting and ending bins appropriately
    df['birth_weight_start'] = df.birth_weights.shift(periods=1, fill_value=0.0)
    df['birth_weight_end'] = df.birth_weights
    df['birth_weight_end'].iloc[-1] = LARGER_THAN_LARGEST_BABY_ON_RECORD
    df['value'] = df.index / len(df)

    # clean up the sim, drop the redundant column
    del sim
    df = correct_support_values(df)
    return df.drop('birth_weights', axis=1)


def correct_support_values(df):
    if 0.0 == df.value.iloc[0]:
        df.value.iloc[0] = df.value.iloc[1] / 2.0
    if 1.0 == df.value.iloc[-1]:
        df.value.iloc[-1] = df.value.iloc[-2] + (1.0 - df.value.iloc[-2]) / 2.0
    return df



def build_bw_rc_data(template: str, location: str, output_dir: str):
    """Writes model specifications from a template and location that
    are used to produce birth weight propensities and ranked bins.

    Parameters
    ----------
    template
        String path to the model specification template file.
    location
        Location to generate the model specification for. Must be a
        location configured in the project ``globals.py``.
    output_dir
        String path to the output directory where the model specification(s)
        will be written.

    Raises
    ------
    ValueError
        If the provided location in not ``'all'`` or is not one of the
        locations configured in the project ``globals.py``.

    """
    build_model_specifications(template, location, output_dir, '_bw_risk_corr')
    bw_risk_corr_spec = Path(output_dir) / f'{sanitize_location(location)}_bw_risk_corr.yaml'
    df = create_bw_rc_data(str(bw_risk_corr_spec))
    bw_risk_corr_spec.unlink()
    return df
