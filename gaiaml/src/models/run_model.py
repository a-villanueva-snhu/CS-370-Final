## The Core model for the GaiaML project. 
# Takes a trained model and uses it to make predictions on new data.
# It is used by the other files in the project to make predictions on new data.


import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from data.database.sqlite import db as db
from config import config_manager

# This is used to track the version of the model in the versioning database for post-hoc analysis.
model_version = config_manager.get_config_value("model_version", default="1.0.0")

## Pull trained model from the versioning database and use it to make predictions on new data.
model = db.load_model_from_versioning(model_version)

# Injest cleaned DR3 random data
rd = db.fetch_data("gaia_data", as_dataframe=True)  # Fetch data from the database

# Run extreme gradient boosting model on the data

# Evaluate the model for internal validation
# Include testing against known hosts

# Save the model to the versioning database

# export the prediction data to the database

