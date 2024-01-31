from utils.config_helper import TAGGING_API
from enum import Enum

# The TagTypes class lists the valid tags that can be requested
class TagTypes(Enum):
    # Define different types of tags
    CONTENT_TYPE = "CONTENT TYPE"
    CONTENT_TYPE_V2 = "CONTENT TYPE V2"
    POPULARITY = "HIT POTENTIAL"
    GENRE = "GENRE"
    GENRE_V2 = "GENRE V2"
    GENRE_V3 = "GENRE V3"
    MOOD = "MOOD"
    MOOD_V3 = "MOOD V3"
    BPM = "BPM"
    BPM_V2 = "BPM V2"
    KEY = "KEY"
    KEY_SHARP = "KEY SHARP"
    KEY_FLAT = "KEY FLAT"
    ENERGY = "ENERGY"
    INSTRUMENTATION = "INSTRUMENTATION"
    INSTRUMENTATION_V2 = "INSTRUMENTATION V2"
    SILENCE_START_STOP = "SILENCE DETECTION GQ8EM03XB2"
    VOCAL_START_STOP = "VOCAL DETECTION LX9DO2R0W3"
    MOOD_BMG = "MOOD NKR57TJ6HU"
    PROFILE_BMG = "PROFILE 6YCG3XQ2WU"
    GENRE_BMG = "GENRE B2KBK7Q822"
    INSTRUMENTATION_BMG = "INSTRUMENTATION 56R2ZUF6KX"
    USE_CASE = "USE CASE"

    @staticmethod
    def getList():
        # Get a list of all tag values
        return [tag.value for tag in TagTypes]

# The tagContent class defines the tag headers and the max number of tags returned by the API for every tag type
class TagContent:
    CONTENT = {
        TagTypes.CONTENT_TYPE: [("CONTENT TYPE", 1), ("QUALITY", 1)],
        TagTypes.CONTENT_TYPE_V2: [("CONTENT TYPE V2", 1), ("QUALITY", 1)],
        TagTypes.POPULARITY: [("HIT POTENTIAL", 1)],
        TagTypes.GENRE: [("GENRE", 1), ("GENRE SECONDARY", 1)],
        TagTypes.GENRE_V2: [("GENRE V2", 4)],
        TagTypes.GENRE_V3: [("GENRE V3", 4)],
        TagTypes.MOOD: [("MOOD", 1), ("MOOD SECONDARY", 1), ("MOOD VALENCE", 1)],
        TagTypes.MOOD_V3: [("MOOD V3", 5), ("MOOD V3 DESCRIPTOR", 5)],
        TagTypes.BPM: [("BPM", 1), ("BPM ALT", 1), ("BPM VARIATION", 1)],
        TagTypes.BPM_V2: [("BPM", 1), ("BPM ALT", 1), ("BPM VARIATION V2", 1)],
        TagTypes.ENERGY: [("ENERGY", 1), ("ENERGY VARIATION", 1)],
        TagTypes.KEY: [("KEY", 1), ("KEY SECONDARY", 1)],
        TagTypes.KEY_FLAT: [("KEY FLAT", 1), ("KEY FLAT SECONDARY", 1)],
        TagTypes.KEY_SHARP: [("KEY SHARP", 1), ("KEY SHARP SECONDARY", 1)],
        TagTypes.INSTRUMENTATION: [("INSTRUMENTATION", 1), ("VOCAL PRESENCE", 1), ("VOCAL GENDER", 1),
                                   ("INSTRUMENT", 5)],
        TagTypes.INSTRUMENTATION_V2: [("INSTRUMENT V2", 5)],
        TagTypes.SILENCE_START_STOP: [("SOUND START (-60DB)", 1), ("SOUND START (-30DB)", 1), ("SOUND STOP (-30DB)", 1),
                                      ("SOUND STOP (-60DB)", 1)],
        TagTypes.VOCAL_START_STOP: [("VOCAL START", 1), ("VOCAL STOP", 1)],
        TagTypes.MOOD_BMG: [("BMG MOOD", 7)],
        TagTypes.PROFILE_BMG: [("BMG PROFILE", 4)],
        TagTypes.GENRE_BMG: [("BMG GENRE", 3)],
        TagTypes.INSTRUMENTATION_BMG: [("BMG INSTRUMENT", 6)],
        TagTypes.USE_CASE: [("USE CASE", 4)]
    }

    @staticmethod
    def getKeyList(tag_type):
        # Get the list of keys for a specific tag type
        return TagContent.CONTENT[tag_type]

# define the valid tags that can be requested
VALID_TAGS = TagTypes.getList()

if TAGGING_API == 'PRODUCTION':
    BASE_URL = "https://api-us.musiio.com"
    KEY = ""
elif TAGGING_API == 'TEST':
    BASE_URL = "https://api-eu.musiiotest.com"
    KEY = ""

TAG_URL = BASE_URL + "/api/v1/extract/tags"

UPLOAD_URLS = {'audio_link': BASE_URL + "/api/v1/upload/audio-link",
               'youtube_link': BASE_URL + "/api/v1/upload/youtube-link",
               'local_file': BASE_URL + "/api/v1/upload/file"}

GENERATE_TAGS_LOG = "GenerateTagsLog"

N_RETRIES = 5
