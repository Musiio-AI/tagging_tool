# Import necessary modules
import argparse
import os
import shutil

from utils.constants import GENERATE_TAGS_LOG
from generate_tags import Tagger
from utils.config_helper import TAGS
from utils.logging_helpers import get_logger
from tags_to_csv import sortTags
import platform
import time

# Get the logger for generating tags
logger = get_logger(GENERATE_TAGS_LOG)

if __name__ == '__main__':
    # Create an argument parser - to handle command line arguments
    parser = argparse.ArgumentParser(description='Sort Tags')

    # Add command line arguments
    parser.add_argument('--source-path', dest='source_path',
                        help='The path to the folder containing tracks to be tagged, '
                             'or a csv with URLs/local path to the tracks to be tagged. If none '
                             'is specified, the script runs in test mode.')

    parser.add_argument('--json-destination-path', dest='json_destination_path',
                        help='The path where individual json tag files will be saved. If none '
                        'is specified, a temporary folder is created and deleted after generating the csv.')

    parser.add_argument('--csv-destination-path', dest='csv_destination_path', default='csv',
                        help='The path to where the csv file will be written.')

    # Parse the command line arguments
    args = parser.parse_args()

    # If no source_path is provided, the script runs in test mode.
    if args.source_path is None:
        logger.info("No --source-path argument was provided. Running script on test files.")
        if platform.system() in ['Linux', 'Darwin']:
            source_path = './test_files/test_input-Unix.csv'
        elif platform.system() in ['Windows']:
            source_path = './test_files/test_input-Windows.csv'
        tags_destination_path = './tags/'

    else:
        source_path = args.source_path

    # If no --json-destination-path is specified, a temporary one is created and deleted after generating the csv.
    if args.json_destination_path is None:
        logger.info("No --json-destination-path was provided. A temporary one will be created and deleted after generating the csv.")
        json_destination_path = "tags-" + time.strftime("%Y%m%d-%H%M%S")
        try:
            os.makedirs(json_destination_path, exist_ok=False)
        except FileExistsError:
            logger.info("The temporary json_destination_path {} already exists. Stopping here to prevent overwriting.")
            exit()
    else:
        json_destination_path = args.json_destination_path

    # Create an instance of the Tagger class
    tagger = Tagger()

    # Tag the files and generate individual json tag files
    tagger.tagFilesTask(source_path=source_path, destination_path=json_destination_path, tag_selection=TAGS)

    # Sort the tags and generate the csv file
    sortTags(tags_path=json_destination_path, tags_csv=args.csv_destination_path, tags_types=TAGS)

    # If no --json-destination-path is specified, delete the temporary folder
    if args.json_destination_path is None:
        shutil.rmtree(json_destination_path)
