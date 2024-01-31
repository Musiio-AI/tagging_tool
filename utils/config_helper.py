import json

# Load the configuration from the "config.json" file
with open("config.json", 'r') as t:
    config = json.load(t)

# Retrieve the value of "tagging_api" from the configuration
TAGGING_API = config["tagging_api"]

# Check if the value of "tagging_api" is either "PRODUCTION" or "TEST"
if TAGGING_API not in ["PRODUCTION", "TEST"]:
    raise Exception('Check your config file: "tagging_api" must be set to "PRODUCTION" or "TEST".')

# Retrieve the value of "log_level" from the configuration
LOG_LEVEL = config["log_level"]

# Check if the value of "log_level" is a valid log level
if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise Exception('Check your config file: "log_level" is not valid.')

# Retrieve the value of "n_processes" from the configuration
N_PROCESSES = config["n_processes"]

# Check if the value of "n_processes" is a numeric string
if not N_PROCESSES.isnumeric():
    raise Exception('Check your config file: "n_processes" should be an integer.')
else:
    # Convert the value of "n_processes" to an integer
    N_PROCESSES = int(N_PROCESSES)

# Evaluate the value of "tags" as a Python expression, using an empty dictionary as the globals
TAGS = eval(config["tags"], {'__builtins__': None}, {})
