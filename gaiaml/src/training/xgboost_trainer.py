## Takes in training data and trains an XGBoost model on it. 
# It is used by the other files in the project to train the 
# model for later predictions.
# It is also used to save and load the model from the 
# versioning database.

from data.database.sqlite import db as db
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from config import config_manager
from logs import logger
from preprocessing.preprocessor import preprocess_data


## -- TRAINING FUNCTION -- ##
def train_xgboost_model(X, y, model_params=None, test_size=0.2, random_state=42):
    """
    Trains an XGBoost model on the provided training data.

    Parameters:
    - X: Features (numpy array or pandas DataFrame)
    - y: Target variable (numpy array or pandas Series)
    - model_params: Dictionary of parameters for the XGBoost model
    - test_size: Proportion of the dataset to include in the test split
    - random_state: Random seed for reproducibility

    Returns:
    - model: Trained XGBoost model
    - X_test: Test features
    - y_test: Test target variable
    """
    
    if len(X) < 2:
        raise ValueError("At least two training rows are required to train a model.")

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Create an XGBoost DMatrix for training
    dtrain = xgb.DMatrix(X_train, label=y_train)
    
    # Set default parameters if none are provided
    if model_params is None:
        unique_targets = np.unique(y_train)
        is_binary_classification = len(unique_targets) == 2 and set(unique_targets).issubset({0, 1})

        model_params = {
            'objective': 'binary:logistic' if is_binary_classification else 'reg:squarederror',
            'eval_metric': 'logloss' if is_binary_classification else 'rmse',
            'max_depth': 6,
            'eta': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'seed': random_state
        }

    # Train the model
    model = xgb.train(model_params, dtrain)

    # Export to JSON for the database versioning system
    model_version = config_manager.get_next_model_version()
    model.save_model("xgboost_model.json")

    db.save_model_version_json(
        version=model_version,
        date_created=config_manager.get_current_date(),
        accuracy=None,  # Replace with actual accuracy if available
        precision=None,  # Replace with actual precision if available
        recall=None,  # Replace with actual recall if available
        model_json="xgboost_model.json"
    )

    return model, X_test, y_test