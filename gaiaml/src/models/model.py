## The Core model for the GaiaML project. 
# It contains the main logic for the project, including the
# training and evaluation of the model. It is used by the 
# other files in the project to run the model and make 
# predictions. It is also used to save and load the 
# model from the versioning database.

import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# This is used to track the version of the model in the versioning database for post-hoc analysis.
model_version = '0.0.1'

# Injest cleaned DR3 data

# Run extreme gradient boosting model on the data

# Evaluate the model for internal validation
# Include testing against known hosts

# Save the model to the versioning database

# export the prediction data to the database