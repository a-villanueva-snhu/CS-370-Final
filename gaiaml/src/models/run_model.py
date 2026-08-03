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
model_json: str | None = db.load_model_from_versioning(model_version)
model: xgb.Booster = xgb.Booster()

# Injest cleaned DR3 random data
rd: pd.DataFrame = db.fetch_data("gaia_dr3_data", as_dataframe=True)  # Fetch data from the database

# Run extreme gradient boosting model on the data
if model_json is not None:
    model.load_model(model_json)  # Load the trained model
else:
    raise ValueError(f"Failed to load model version {model_version} from versioning database")

# -- Evaluate the model for internal validation -- #

# make predictions on the new data
s_prediction: np.ndarray = model.predict(xgb.DMatrix(rd.drop(columns=["source_id"])))
# store the predictions in the database for later analysis
db.store_predictions("gaia_dr3_data_predictions", s_prediction)

# F1 score, precision, recall, and accuracy can be calculated here if needed.



# Include testing against known hosts


# Save the model to the versioning database

# export the prediction data to the database

