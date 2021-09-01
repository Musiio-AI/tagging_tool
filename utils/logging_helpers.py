from utils.config_helper import LOG_LEVEL
import logging


def get_logger(logger_name):

    # create logger for prd_ci
    logger = logging.getLogger(logger_name)

    if not len(logger.handlers):
        logger.setLevel(level=LOG_LEVEL)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Create console handler for logger.
        ch = logging.StreamHandler()
        ch.setLevel(level=LOG_LEVEL)
        ch.setFormatter(formatter)

        logger.addHandler(ch)
    return logger
