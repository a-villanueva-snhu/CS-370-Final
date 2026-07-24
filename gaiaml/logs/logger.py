## A simple logging utility for the GaiaML project.

import logging

_TEST = True  # Set to False in production

# Configure the logger
logging.basicConfig(
    level=logging.ERROR, 
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gaiaml.log"),
        logging.StreamHandler()
    ]
)

## API functions for using this file as a logger
def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

## Test the logger
def test_logger():
    if not _TEST:
        return  # Skip test logging if not in test mode

    try:
        bad_action = 1 / 0
    except ZeroDivisionError as e:
        logging.exception("An exception occurred: %s", e)
