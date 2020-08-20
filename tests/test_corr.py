import numpy as np, pandas as pd, scipy.stats
from vivarium import InteractiveContext

STUNTING_MEAN = 0.394
WASTING_MEAN = 0.308


def test_corr_bw_haz():

    # how to check this?
    # use vivarium.InteractiveContext to synthesize a population
    yaml_file_name = 'src/vivarium_gates_bep/model_specifications/india.yaml'  # need to create this with make_specs program
    sim = InteractiveContext(yaml_file_name)
    sim.step(step_size=pd.Timedelta(days=30))
    
    # get the correlation coefficient of bw and haz
    pop = sim.get_population()
    bw = pop.birth_weight

    pipe_stunting = sim.get_value('child_stunting.exposure')
    stunting_z = pipe_stunting(pop.index, skip_post_processor=True)

    pipe_wasting = sim.get_value('child_wasting.exposure')
    wasting_z = pipe_wasting(pop.index, skip_post_processor=True)

    corr_stunting = scipy.stats.spearmanr(bw, stunting_z).correlation
    corr_wasting = scipy.stats.spearmanr(bw, wasting_z).correlation

    # check if it is sufficiently close to the expected value
    assert np.abs(corr_stunting - STUNTING_MEAN) <= .10, f'{corr_stunting} not close enough to {STUNTING_MEAN}'
    assert np.abs(corr_wasting - WASTING_MEAN) <= .10, f'{corr_wasting} not close enough to {WASTING_MEAN}'


test_corr_bw_haz()
