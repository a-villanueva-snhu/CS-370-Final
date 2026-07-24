""" Runtime logger for GaiaML """
## This module provides logging functionality for the GaiaML project. 
# It logs model runtime statistics, errors, and other relevant information to an rt_log file.

import logging
import os

_TEST = True

# Configure the logger
log_file = "rt_log.log"

logger = logging.getLogger('gaiaml_runtime')
logger.setLevel(logging.INFO)
logger.propagate = False

log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
log_dir = os.path.normpath(log_dir)

os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, log_file)

file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
stream_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)

stream_handler.setFormatter(formatter) 

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def cleanup_rtlogger():
    """ Clean up the logger handlers when the program exits """
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)
