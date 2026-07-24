## A simple logging utility for the GaiaML project.

import logging

_TEST = True  # Set to False in production

# Configure the logger
logger = logging.getLogger('gaiaml')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('gaiaml/logs/gaiaml.log', mode='a')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

## API functions for using this file as a logger
def log_info(message):
    logger.info(message)
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

## Test the logger
def internal_test_logger():
    if not _TEST:
        return  # Skip test logging if not in test mode

    try:
        bad_action = 1 / 0
    except ZeroDivisionError as e:
        logging.exception("An exception occurred: %s", e)
