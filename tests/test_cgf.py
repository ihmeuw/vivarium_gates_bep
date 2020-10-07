import sys
import numpy as np, pandas as pd, scipy.stats
from vivarium import InteractiveContext, Artifact

DRAW='draw_0'

TIME_FIRST = 29
TIME_SECOND =366-TIME_FIRST

AGE_FIRST=(0.07671, 1.0)
AGE_SECOND=(1.0, 5.0)

ROUND_TO = 4

def trans(inp, round_to):
    return (inp - 10.0).round(round_to)

ARTIFACT='/share/costeffectiveness/artifacts/vivarium_gates_bep/{}.hdf'

def get_artifact_data(artifact):
    art = Artifact(artifact)
    df_wasting = art.load('alternative_risk_factor.child_wasting.exposure')
    df_stunting = art.load('alternative_risk_factor.child_stunting.exposure')
    return df_stunting, df_wasting


def comp_data(art_stunting, art_wasting, model_stunting, model_wasting, age_start, age_end):
    art_s_mean = art_stunting.query('age_start >= {} and age_end <= {}'.format(age_start, age_end)).get(DRAW).mean()
    ms_mean = model_stunting.mean()
    art_s_mean = trans(art_s_mean, ROUND_TO)
    ms_mean = trans(ms_mean, ROUND_TO)
    print(f'Artifact stunting mean = {art_s_mean} versus Model mean {ms_mean}')
    art_s_median = art_stunting.query('age_start >= {} and age_end <= {}'.format(age_start, age_end)).get(DRAW).median()
    ms_median = model_stunting.median()
    art_s_median = trans(art_s_median, ROUND_TO)
    ms_median = trans(ms_median, ROUND_TO)
    print(f'Artifact stunting median = {art_s_median} versus Model median {ms_median}')

    aw_mean = art_wasting.query('age_start >= {} and age_end <= {}'.format(age_start, age_end)).get(DRAW).mean()
    mw_mean = model_wasting.mean()
    aw_mean = trans(aw_mean, ROUND_TO)
    mw_mean = trans(mw_mean, ROUND_TO)
    print(f'Artifact wasting mean = {aw_mean} versus Model mean {mw_mean}')
    aw_median = art_wasting.query('age_start >= {} and age_end <= {}'.format(age_start, age_end)).get(DRAW).median()
    mw_median = model_wasting.median()
    aw_median = trans(aw_median, ROUND_TO)
    mw_median = trans(mw_median, ROUND_TO)
    print(f'Artifact wasting median = {aw_median} versus Model mean {mw_median}')


def test_cgf(art_stunting, art_wasting):
    yaml_file_name = 'src/vivarium_gates_bep/model_specifications/india.yaml'  # need to create this with make_specs program
    sim = InteractiveContext(yaml_file_name)
    pipe_stunting = sim.get_value('child_stunting.exposure')
    pipe_wasting = sim.get_value('child_wasting.exposure')

    for param in [(TIME_FIRST, AGE_FIRST), (TIME_SECOND, AGE_SECOND)]:
        print(f'Days == {param[0]}')
        sim.step(step_size=pd.Timedelta(days=param[0]))
        pop = sim.get_population().query('alive=="alive"')
        print(f'Pop len = {len(pop)}')
        stunting_z = pipe_stunting(pop.index, skip_post_processor=True)
        wasting_z = pipe_wasting(pop.index, skip_post_processor=True)
        comp_data(art_stunting, art_wasting, stunting_z, wasting_z, param[1][0], param[1][1])

ac = len(sys.argv)
country = 'india'
if 2 == ac:
    country = sys.argv[1].lower()

art_stunting, art_wasting = get_artifact_data(ARTIFACT.format(country))
test_cgf(art_stunting, art_wasting)
