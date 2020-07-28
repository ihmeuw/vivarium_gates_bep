import numpy as np, pandas as pd, scipy.stats
from vivarium import InteractiveContext

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
    haz = pipe_stunting(pop.index, skip_post_processor=True)

    corr = scipy.stats.spearmanr(bw, haz).correlation

    # check if it is sufficiently close to the expected value

    assert np.abs(corr - .3) <= .05, 'expect correlation to be close to 0.3'




