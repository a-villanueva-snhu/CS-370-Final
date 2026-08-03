## Checks preprocessed data for confirmed exoplanet hosts
# against the confirmed hosts in the database. 
# This is used to validate the model's predictions and 
# ensure that the preprocessing step has not introduced any 
# errors or inconsistencies.

import logs.logger as logger
from data.database.sqlite import db as db

