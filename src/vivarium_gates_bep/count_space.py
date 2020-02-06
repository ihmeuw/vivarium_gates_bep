import os
import pandas as pd
import re

from pathlib import Path
from typing import Dict

from vivarium_gates_bep import globals as project_globals

OUTPUT_FOLDER_NAME = 'count_space'
FIELD_REGEX = '{([A-Z_]+)}'
EXCLUDE_TEMPLATES = [
    # TODO: do something with the non-count space template
    'z_scores',
    'birth_weight',
    'gestational_age',
]


def create_field_regex(field_name: str) -> str:
    field_values = [field.lower() for field in project_globals.TEMPLATE_FIELD_MAP[field_name]]
    return f"((?:{')|(?:'.join(field_values)}))"


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


def create_count_space_data_for_single_columns(raw_output: pd.DataFrame) -> pd.DataFrame:
    column_names = [column for column in project_globals.SINGLE_COLUMNS
                    if column != project_globals.MALNOURISHED_MOTHERS_PROPORTION_COLUMN]
    df = pd.DataFrame(raw_output[['input_draw'] + column_names].groupby('input_draw').sum().stack(), columns=['count'])
    df.reset_index(inplace=True)
    df.rename({'level_1': 'property'}, axis=1, inplace=True)
    df.set_index(['input_draw', 'property'], inplace=True)
    return df


def create_count_space_data_for_template(raw_output: pd.DataFrame, template_name: str) -> pd.DataFrame:
    template_string = project_globals.COLUMN_TEMPLATES[template_name]
    field_names = [s.lower() for s in re.findall(FIELD_REGEX, template_string)]

    column_names = [column_name.lower() for column_name in project_globals.RESULT_COLUMNS(template_name)]
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


def create_count_space_data_as_dict(raw_output_path: str) -> Dict[str, pd.DataFrame]:
    raw_output = pd.read_hdf(raw_output_path)
    raw_output.reset_index(drop=True, inplace=True)
    count_space_data = {
        template_name: create_count_space_data_for_template(raw_output, template_name)
        for template_name in project_globals.COLUMN_TEMPLATES if template_name not in EXCLUDE_TEMPLATES
    }
    count_space_data['standard'] = create_count_space_data_for_single_columns(raw_output)

    return count_space_data


def create_count_space_data_from_hdf(hdf_path: str) -> None:
    raw_output = pd.read_hdf(hdf_path)
    raw_output.reset_index(drop=True, inplace=True)
    output_dir = Path(os.path.dirname(hdf_path)) / OUTPUT_FOLDER_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    for template_name in project_globals.COLUMN_TEMPLATES:
        if template_name not in EXCLUDE_TEMPLATES:
            count_space_df = create_count_space_data_for_template(raw_output, template_name)
            count_space_df.to_csv(output_dir / f'{template_name}.csv')
            count_space_df.to_hdf(output_dir / f'{template_name}.hdf', template_name)

    single_columns_df = create_count_space_data_for_single_columns(raw_output)
    single_columns_df.to_csv(output_dir / 'single_columns.csv')
    single_columns_df.to_hdf(output_dir / 'single_columns.hdf', 'single_columns')


def create_count_space_data_for_all_outputs(root_directory: str) -> None:
    for subdir, dirs, files in os.walk(root_directory):
        if 'output.hdf' in files:
            create_count_space_data_from_hdf(Path(subdir) / 'output.hdf')
