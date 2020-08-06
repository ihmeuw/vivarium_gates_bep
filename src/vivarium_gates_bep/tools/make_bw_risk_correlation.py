"""Application functions for producing specification files from which we derive birth weight risk correlation."""
import numpy as np
import pandas as pd

from pathlib import Path

from vivarium import InteractiveContext
from vivarium_gates_bep.tools.make_specs import build_model_specifications


LARGER_THAN_LARGEST_BABY_ON_RECORD = 25 * 454


def empirical_percentile(x, samples):
    return np.mean(x >= samples)


def create_bw_rc_data(spec_file: str):
    sim = InteractiveContext(spec_file)
    df = pd.DataFrame()
    df['birth_weights'] = sim.get_population().birth_weight

    # rank birth weights
    df['birth_weight_percentile'] = df.birth_weights.apply(empirical_percentile, samples=df.birth_weights)
    df = df.sort_values(by=['birth_weight_percentile'])

    # create upper and lower bounds, fill starting and ending bins appropriately
    df['bw_lower_bound'] = df.birth_weights.shift(periods=1, fill_value=0.0)
    df['bw_upper_bound'] = df.birth_weights
    df.bw_upper_bound.iloc[-1] = LARGER_THAN_LARGEST_BABY_ON_RECORD

    # drop the redundant column and write the output file
    df = df.drop('birth_weights', axis=1)
    outfile = f'{Path(spec_file).stem}.csv'
    df.to_csv(outfile, index=False)
    del sim


def build_bw_rc_data(template: str, location: str, output_dir: str):
    """Writes model specifications from a template and location that
    are used to produce birth weight propensities and ranked bins.

    Parameters
    ----------
    template
        String path to the model specification template file.
    location
        Location to generate the model specification for. Must be a
        location configured in the project ``globals.py`` or ``'all'``
        to generate all model specifications.
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
    bw_risk_corr_specs = Path(output_dir).glob('*_bw_risk_corr.yaml')
    for loc in bw_risk_corr_specs:
        create_bw_rc_data(str(loc))
