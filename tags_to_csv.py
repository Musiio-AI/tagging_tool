import os
import csv
import json
import argparse

from utils.config_helper import TAGS
from utils.constants import VALID_TAGS, TagTypes, TagContent


def getTagsInFolder(tags_path):
    """
    Check the provided folder for json files and return it in a list
    :param tags_path: string - The path where tag jsons are stored
    :return: tags: list - A list containing the paths to each tag json
    """

    if not os.path.isdir(tags_path):
        e = 'ERROR: The system cannot find the path specified: {}'.format(tags_path)
        print(e)
        return ValueError(e)

    tags = list()

    for file in os.listdir(tags_path):
        if file[-5:] == ".json":
            tags.append(file)

    if len(tags) == 0:
        e = 'ERROR: No tags found in the provided folder'
        print(e)
        return ValueError(e)

    return tags


def checkValidTags(tags_types):
    """
    Check if the tag types provided by the user are valid Musiio tags
    :param tags_types: string - The tag types to extract from each tag json file
    """

    tags_types = list(map(lambda x: x.upper(), tags_types))

    if len(tags_types) == 0:
        e = 'ERROR: No Tags Provided'
        print(e)
        return ValueError(e)

    for tag in tags_types:
        if tag not in VALID_TAGS:
            e = 'ERROR: "{}" is not a valid tag name'.format(tag)
            print(e)
            return ValueError(e)

    return tags_types

def writeTags(csv_writer, tags_path, file, keys):
    """
    Opens a given json file, checks through the given tag types, and writes it to the CSV file

    :param csv_writer: csv writer object
    :param tags_path: string - The path where tag json files are stored
    :param file: file - output csv file
    :param keys: list - list of tag types to check

    :return: None
    """

    # Open the json file
    with open(tags_path + '/' + file, 'r') as t:
        values = list()

        # Load the content of the json file
        content = json.load(t)
        values.append(content["feature_id"])
        values.append(content["file_name"])
        tags = content["tags"]

        # Iterate through the given tag types
        for key in keys:
            tag_exists = False

            # Iterate through the tags in the json file
            for index, tag in enumerate(tags):
                if tag["type"] == key:
                    values.append(tag["name"])
                    values.append(tag["score"])
                    tag_exists = True

                    # Remove the tag from the list to avoid duplicate entries
                    tags.pop(index)
                    break

            # If the tag type doesn't exist, append empty values
            if not tag_exists:
                values.append("")
                values.append("")

        # Write the values to the CSV file
        csv_writer.writerow(values)


def sortTags(tags_path, tags_csv, tags_types):
    """
    Generate a CSV file of all the tags located in the provided folder
    :param tags_path: string - The path where tag jsons are stored
    :param tags_csv: string - The path where csv file will be saved
    :param tags_types: string - The tag types to extract from each tag json file
    :param progress: tkinter Progressbar type object. Only used in GUI
    """

    # check if tag names provided by the user are valid
    tags_types = checkValidTags(tags_types)
    if type(tags_types) == ValueError:
        return ValueError(tags_types)

    # Built the set of TagTypes objects from the use tags_types list
    tag_list = set([TagTypes(tag) for tag in tags_types])

    keys = list()
    headers = ["URL_FILENAME", "MUSIIO TMP ID"]

    for tag in tag_list:
        content = TagContent.getKeyList(tag)
        for key, count in content:
            for _ in range(count):
                keys.append(key)
                headers.append(key)
                headers.append("SCORE")

    # get all valid tag json files from the path provided
    tags = getTagsInFolder(tags_path)
    if type(tags) == ValueError:
        return ValueError(tags)

    # Check if destination path is valid
    if not os.path.isdir(tags_csv):
        os.makedirs(tags_csv, exist_ok=True)
    tags_csv = os.path.join(tags_csv, 'tags.csv')

    with open(tags_csv, 'w', newline='') as csv_file:

        # creates headers
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(headers)

        # iterate through tags in the folder
        for file in tags:
            writeTags(csv_writer, tags_path, file, keys)


# This code block is the main entry point of the script.
# It uses the argparse module to parse command line arguments.
# The arguments include:
# - --tags-path: The path to the folder containing tags
# - --tags-csv: The path to where the CSV file will be written (default is 'csv')
# - --tags-types: The type of tags to extract from each file (default is TAGS constant)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate CSV File Containing Tags')

    parser.add_argument('--tags-path', dest='tags_path',
                        help='The path to the folder containing tags')

    parser.add_argument('--tags-csv', dest='tags_csv', default='csv',
                        help='The path to where csv file will be written')

    parser.add_argument('--tags-types', nargs='+', dest='tags_types', default=TAGS,
                        help='The type of tags to extract from each file')

    args = parser.parse_args()

    # Calls the sortTags function with the provided command line arguments
    sortTags(tags_path=args.tags_path, tags_csv=args.tags_csv, tags_types=args.tags_types)