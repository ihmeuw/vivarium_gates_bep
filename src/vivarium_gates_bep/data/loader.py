"""Loads, standardizes and validates input data for the simulation."""
import pandas as pd
from vivarium.framework.artifact import EntityKey


def get_data(lookup_key: EntityKey, location: str) -> pd.DataFrame:
    raise NotImplementedError
