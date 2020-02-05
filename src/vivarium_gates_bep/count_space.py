import pandas as pd
import re

from typing import Dict

from vivarium_gates_bep import globals as project_globals

FIELD_REGEX = '{([A-Z_]+)}'


def create_field_regex(field_name: str) -> str:
    return f"((?:{')|(?:'.join(project_globals.TEMPLATE_FIELD_MAP[field_name])}))"


def create_template_regex(template_name: str) -> str:
    template_string = project_globals.COLUMN_TEMPLATES[template_name]
    field_names = re.findall(FIELD_REGEX, template_string)
    regex_fields = {field: create_field_regex(field) for field in field_names}

    template_regex = template_string
    for field, field_regex in regex_fields.items():
        template_regex = template_regex.replace(f'{{{field}}}', field_regex)
    if len(field_names) == 1:
        template_regex += '()'
    return template_regex


def create_count_space_data_for_standard_columns(raw_output: pd.DataFrame) -> pd.DataFrame:
    column_names = list(project_globals.STANDARD_COLUMNS.values())
    df = pd.DataFrame(raw_output[['input_draw'] + column_names].groupby('input_draw').sum().stack(), columns=['count'])
    df.reset_index(inplace=True)
    df.rename({'level_1': 'property'}, axis=1, inplace=True)
    df.set_index(['input_draw', 'property'], inplace=True)
    return df


def create_count_space_data_for_template(raw_output: pd.DataFrame, template_name: str) -> pd.DataFrame:
    template_string = project_globals.COLUMN_TEMPLATES[template_name]
    field_names = [s.lower() for s in re.findall(FIELD_REGEX, template_string)]

    column_names = project_globals.RESULT_COLUMNS(template_name)
    template_regex = create_template_regex(template_name)

    df = pd.DataFrame(raw_output[['input_draw'] + column_names].groupby('input_draw').sum().stack(),
                      columns=[template_name])
    df.reset_index(inplace=True)

    for i, field_name in enumerate(field_names):
        df[field_name] = pd.Series([re.findall(template_regex, df.at[row, 'level_1'])[0][i] for row in df.index],
                                   df.index)

    del df['level_1']
    df.set_index(['input_draw'] + field_names, inplace=True)
    return df


def create_count_space_data(raw_output_path: str) -> Dict[str, pd.DataFrame]:
    raw_output = pd.read_hdf(raw_output_path)
    raw_output.reset_index(drop=True, inplace=True)
    count_space_data = {
        template_name: create_count_space_data_for_template(raw_output, template_name)
        for template_name in project_globals.COLUMN_TEMPLATES
        # TODO: the transition columns in the output.hdf don't match globals.py
        # Exclude non-count data
        if template_name not in ['z_scores', 'birth_weight', 'gestational_age', 'transition_count']
    }
    count_space_data['standard'] = create_count_space_data_for_standard_columns(raw_output)

    return count_space_data
