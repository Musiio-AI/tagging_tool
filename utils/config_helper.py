import json

with open("config.json", 'r') as t:
    config = json.load(t)

TAGGING_API = config["tagging_api"]
if TAGGING_API not in ["PRODUCTION", "TEST"]:
    raise Exception('Check your config file: "tagging_api" must be set to "PRODUCTION" or "TEST".')

LOG_LEVEL = config["log_level"]
if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise Exception('Check your config file: "log_level" is not valid.')


N_PROCESSES = config["n_processes"]
if not N_PROCESSES.isnumeric():
    raise Exception('Check your config file: "n_processes" should be an integer.')
else:
    N_PROCESSES = int(N_PROCESSES)

TAGS = eval(config["tags"], {'__builtins__': None}, {})
