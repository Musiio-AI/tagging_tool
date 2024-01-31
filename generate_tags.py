import os
import json
import codecs
import requests
import argparse
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_unless_exception_type
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
from functools import partial
from utils.config_helper import TAGS, N_PROCESSES, TAGGING_API
from utils.constants import KEY, TAG_URL, UPLOAD_URLS, GENERATE_TAGS_LOG, N_RETRIES
from utils.logging_helpers import get_logger
from pathlib import Path


logger = get_logger(GENERATE_TAGS_LOG)

os.makedirs("log", exist_ok=True)
timestamp = time.strftime("%Y%m%d-%H%M%S")

FAILED_FILE = "log/FAILED-" + timestamp + ".csv"
FAILED_DETAILS_FILE = "log/FAILED_DETAILS-" + timestamp + ".csv"


class Tagger:
    # Initialize the Tagger class
    def __init__(self):
        self.__completed = 0  # Number of completed tasks
        self.__mutex = Lock()  # Mutex lock for thread synchronization

    @staticmethod
    def __checkTagSelection(tag_selection):
        """
        Check whether the tags provided by the user are valid Musiio tags
        :param tag_selection: list - A list containing the type of tags to tag the track for
        :return: tag_selection: list - A list containing the type of tags to tag the track for
        """

        tag_selection = list(map(lambda x: x.upper(), tag_selection))

        for tag in tag_selection:

            if tag not in TAGS:
                e = 'ERROR: "{}" is not a valid tag type'.format(tag)
                print(e)
                return ValueError(e)

        return tag_selection

    @staticmethod
    def __loadData(file_path):
        """
        Load all urls from the specified CSV data set file.
        :return: List of URLs to extract spectrograms for
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError()

        file_type = str(file_path).split(".")[-1]
        if not file_type or file_type != "csv":
            raise Exception("Incorrect file type")

        with codecs.open(file_path, "r", "utf-8") as file:
            data = file.read().replace("\r", "").split("\n")

        data_set = list()
        for entry in data:
            if entry:
                data_set.append(entry.split(",")[0])

        logger.info("Loaded " + str(len(data_set)) + " urls to extract!")
        return data_set

    @staticmethod
    def __listFiles(source_path):
        """
        Recursively check the provided path for audio tracks and return it in a list
        :param source_path: string - The path where audio tracks are stored
        :return: files: list - A list containing the paths to each audio track
        """

        files = []
        for r, d, f in os.walk(source_path):
            for file_name in f:
                if '.m4a' in file_name or '.mp3' in file_name or '.wav' in file_name:
                    line = 'file://' + str(Path(os.path.abspath(source_path)) / Path(file_name))
                    files.append(line)

        if len(files) == 0:
            e = "ERROR: No '.mp3', '.wav', or '.m4a' files found in the provided source folder"
            print(e)
            return ValueError(e)
        print("Loaded " + str(len(files)) + " files to extract!")
        return files

    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=2, min=4, max=60),
           retry=retry_if_exception_type() & retry_unless_exception_type(IOError),
           reraise=True)
    def __uploadFile(self, data, api_key=None):
        """
        Makes a POST request to upload the given audio track
        :param data: string - The path where the audio track is stored
        :param api_key: str - Your API key provided by Musiio
        :return: feature_id: string - A unique ID for this audio track
        """

        file = None
        json = None

        if data.find("file://") > -1:
            UPLOAD_URL = UPLOAD_URLS['local_file']
            f = data.replace("file://", "")
            try:
                file = [('audio', open(Path(f), 'rb'))]
            except IOError as e:
                logger.error("UPLOAD: {}".format(e))
                raise e
            logger.debug('UPLOAD: local file {}'.format(f))
        else:
            json = {'link': data}
            if data.find("youtube") > -1:
                UPLOAD_URL = UPLOAD_URLS['youtube_link']
                logger.debug('UPLOAD: YouTube link {}'.format(data))
            else:
                UPLOAD_URL = UPLOAD_URLS['audio_link']
                logger.debug('UPLOAD: Audio link {}'.format(data))

        # post request to the upload url with file or json & api key
        response = requests.post(UPLOAD_URL, files=file, json=json, auth=(api_key, ""))
        json_data = response.json()
        if response.status_code != 200:
            error_message = "UPLOAD: Response code {} - API error {}".format(response.status_code, json_data['error'])
            logger.error(error_message)
            raise Exception(error_message)

        logger.debug('UPLOAD: Got response {}'.format(json_data))
        feature_id = json_data["id"]
        # return the track id
        return feature_id

    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=2, min=4, max=60),
           reraise=True)
    def __tagFile(self, feature_id, tag_selection, api_key=None):
        """
        Makes a POST request to tag the given audio track
        :param feature_id: string - A unique ID for this audio track
        :param tag_selection: list - A list containing the type of tags to tag the track for
        :param api_key: str - Your API key provided by Musiio
        :return: tags: list - A list of tags for this audio track
        """

        url = TAG_URL
        data = {
            "id": feature_id,
            "tags": tag_selection
        }
        logger.debug('EXTRACT: Request {} with json {}'.format(url, data))
        response = requests.post(url, json=data, auth=(api_key, ""))
        json_data = response.json()

        if response.status_code != 200:
            error_message = "EXTRACT: Response code {} - API error {}".format(response.status_code, json_data['error'])
            logger.error(error_message)
            raise Exception(error_message)

        logger.debug('EXTRACT: Got response {}'.format(json_data))
        tags = json_data["tags"]
        return tags

    def __processFile(self, destination_path, tag_selection, api_key, file_name):
        """
         Uploads the given audio track, tags it, and saves the tags in a json file located in the destination path
         :param destination_path: string - The path where tag json files are saved
         :param tag_selection: list - A list containing the type of tags to tag the track for
         :param api_key: str - Your API key provided by Musiio
         :param file_name: string - The path where the audio track is stored
         :return: 1 if successful, 0 if unsuccessful
         """

        try:
            # call the upload function to get the feature id
            feature_id = self.__uploadFile(file_name, api_key)
        except Exception as e:
            with codecs.open(FAILED_DETAILS_FILE, "a", "utf-8") as file:
                file.write(file_name + ",,Upload failure: " + str(e) + "\n")
            with codecs.open(FAILED_FILE, "a", "utf-8") as file:
                file.write(file_name + "\n")
                return 0
        # get the tags for the feature id
        if feature_id:
            out_content = {"tags": None, "file_name": None, "feature_id": None}
            try:
                # call the tag function to get the tags
                tags = self.__tagFile(feature_id, tag_selection, api_key)
                out_content["tags"] = tags
            except Exception as e:
                with codecs.open(FAILED_DETAILS_FILE, "a", "utf-8") as file:
                    file.write(file_name + "," + feature_id +",Tagging failure: " + str(e) + "\n")
                with codecs.open(FAILED_FILE, "a", "utf-8") as file:
                    file.write(file_name + "\n")
                    return 0

            if file_name.find("file://") > -1:
                # If local file, remove "file://" and path to store only file basename
                file_basename = file_name.replace("file://", "")
                file_basename = os.path.basename(file_basename)
                out_content["file_name"] = file_basename
            else:
                # If URL, store everything
                out_content["file_name"] = file_name
            out_content["feature_id"] = feature_id
            out_file = feature_id + ".json"
            out_path = os.path.join(destination_path, out_file)

            with codecs.open(out_path, "w", "utf-8") as file:
                file.write(json.dumps(out_content))

            return 1

        return 0

    def __tagFiles(self, file_list, destination_path, tag_selection, api_key=None):
        """
         Creates a ThreadPool to tag the given list of audio tracks
         :param file_list: list - A list containing the paths to each audio track
         :param destination_path: string - The path where tag json files are saved
         :param tag_selection: list - A list containing the type of tags to tag the track for
         :param api_key: str - Your API key provided by Musiio
         """

        # Set the number of processes to use (5 set in config.json by default)
        n_processes = N_PROCESSES
        if TAGGING_API == 'TEST':
            logger.debug("Test API is used: set n_processes to 1.")
            n_processes = 1
        elif len(file_list) < N_PROCESSES:
            logger.debug("Limit n_processes to {} based of the number of files to process.".format(len(file_list)))
            n_processes = len(file_list)
        # Create a ThreadPool to tag the files
        with ThreadPool(n_processes) as pool:
            # Create a partial function to pass the destination path, tag selection, and api key to the processFile function
            process = partial(self.__processFile, destination_path, tag_selection, api_key)
            # apply the process function to each file in the file list
            # _ is a discarded variable that is not used
            _ = pool.map(process, file_list)

    def tagFilesTask(self, source_path, destination_path, tag_selection=None, api_key=None):
        """
        Tag tracks in source folder and save the tags in the destination folder
        :param source_path: string - The path where tracks are stored
        :param destination_path: string - The path where tag json files are saved
        :param tag_selection: list - A list containing the type of tags to tag the track for
        :param api_key: str - Your API key provided by Musiio
        """

        # Convert paths str to Path for multiple OS compatibility
        source_path = Path(source_path)
        destination_path = Path(destination_path)

        # Check if destination path is valid
        if not os.path.isdir(destination_path):
            os.makedirs(destination_path, exist_ok=True)

        # Check and list files in source path recursively
        if os.path.isfile(source_path):
            logger.debug('A source csv file was provided. Loading data from it...')
            files = self.__loadData(source_path)
        elif os.path.isdir(source_path):
            logger.debug('A source directory was provided. Listing audio files inside...')
            target_path = Path(source_path)
            files = self.__listFiles(target_path)

        if type(files) == ValueError:
            return ValueError(files)

        logger.debug('{} files/links were found.'.format(len(files)))

        api_key = KEY
        tag_selection = self.__checkTagSelection(tag_selection)
        if type(tag_selection) == ValueError:
            return ValueError(tag_selection)

        # call the tagFiles function to tag the files
        self.__tagFiles(files, destination_path, tag_selection, api_key)



# Check if the current module is being run as the main program
if __name__ == '__main__':

    # Create an argument parser object
    parser = argparse.ArgumentParser(description='Sort Tags')

    # Add command-line arguments
    parser.add_argument('--source-path', dest='source_path',
                        help='The path to the folder containing tracks to be tagged, '
                             'or a csv with URLs/local path to the tracks.')

    parser.add_argument('--destination-path', dest='destination_path',
                        help='The path where json tag files will be saved')

    parser.add_argument('--tag-selection', nargs='+', dest='tag_selection', default=TAGS,
                        help='The type of tags to tag each audio file for.')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Create an instance of the Tagger class
    tagger = Tagger()

    # Call the tagFilesTask method with the provided arguments
    tagger.tagFilesTask(source_path=args.source_path, destination_path=args.destination_path, tag_selection=args.tag_selection)
