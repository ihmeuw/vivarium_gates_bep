from pathlib import Path
import shutil

from loguru import logger

from vivarium_gates_bep.results_processing import process_results


def build_results(output_file: str):
    logger.info(f'Reading in output data from {output_file}.')
    output_file = Path(output_file)
    data = process_results.read_data(output_file)
    data = process_results.aggregate_over_seed(data)
    logger.info(f'Computing count space data.')
    measure_data = process_results.make_measure_data(data)
    measure_dir = output_file.parent / 'count_data'
    if measure_dir.exists():
        shutil.rmtree(measure_dir)
    measure_dir.mkdir(exist_ok=True, mode=0o775)
    measure_data.dump(measure_dir)
