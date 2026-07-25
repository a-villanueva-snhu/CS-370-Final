## A simple logging utility for the GaiaML project.

import logging
import os
from config import config_manager

_TEST = True  # Set to False in production

# Configure from config.yaml if it exists


# Configure the logger
logger = logging.getLogger('gaiaml')
logger.setLevel(logging.INFO)
logger.propagate = False

## Set the log directory and file path
log_file = config_manager.get_config_value("logging.log_file_path", os.path.join(os.getcwd(), "logs", "gaiaml.log"))
log_file = os.path.normpath(log_file)
log_dir = os.path.dirname(log_file)
os.makedirs(log_dir, exist_ok=True)

## Set up the file and stream handlers
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

## Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def __exit__(self, exc_type, exc_value, traceback):
    # Clean up the logger handlers when the program exits
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)


## API functions for using this file as a logger
def log_info(message):
    logger.info(message)


def log_warning(message):
    logger.warning(message)


def log_error(message):
    logger.error(message)


def log_exception(message):
    logger.exception(message)

## Test the logger
def internal_test_logger():
    if not _TEST:
        return  # Skip test logging if not in test mode

    try:
        bad_action = 1 / 0
    except ZeroDivisionError as e:
        log_exception(f"An exception occurred: {e}")
