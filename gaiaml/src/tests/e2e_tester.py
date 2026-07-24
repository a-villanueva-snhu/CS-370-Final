## The main test file for the project. It contains all the 
#  test cases to test the functionality of the project. 
# It is used by the other files in the project to test the 
# functionality of the project. Tests should, generally,
# be designed to be run modularly in isolation, and not 
# depend on other tests.

import unittest
from logs import logger

### Test cases for the GaiaML project ###
# ------------------------------------- #

# Basic test case for testing the logger functionality
class TestLogger(unittest.TestCase):
    def test_log_info(self):
        try:
            logger.log_info("This is an info message for testing.")
        except Exception as e:
            self.fail(f"Logging info failed with exception: {e}")

    def test_log_warning(self):
        try:
            logger.log_warning("This is a warning message for testing.")
        except Exception as e:
            self.fail(f"Logging warning failed with exception: {e}")

    def test_log_error(self):
        try:
            logger.log_error("This is an error message for testing.")
        except Exception as e:
            self.fail(f"Logging error failed with exception: {e}")

    def test_log_exception(self):
        try:
            logger.log_exception("This is an exception message for testing.")
        except Exception as e:
            self.fail(f"Logging exception failed with exception: {e}")

