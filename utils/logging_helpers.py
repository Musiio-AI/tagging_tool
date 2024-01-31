# Import necessary modules
from utils.config_helper import LOG_LEVEL
import logging

# Define a function to get a logger
def get_logger(logger_name):

    # Create logger object
    logger = logging.getLogger(logger_name)

    # Check if logger already has handlers
    if not len(logger.handlers):

        # Set logger level
        logger.setLevel(level=LOG_LEVEL)

        # Create formatter for log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Create console handler for logger
        ch = logging.StreamHandler()
        ch.setLevel(level=LOG_LEVEL)
        ch.setFormatter(formatter)

        # Add console handler to logger
        logger.addHandler(ch)

    # Return the logger
    return logger
