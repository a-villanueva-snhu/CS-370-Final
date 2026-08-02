## Preprocesses raw Gaia Data into a format suitable for 
# machine learning models. This includes cleaning, 
# normalization, and feature engineering.

import pandas as pd
from data.database.sqlite import db as db
import logs.logger as logger


## -- Preprocess Gaia Data -- ##
## Feature Selection and Preprocessing ##
def preprocess_gaia_data(df, target_column='is_confirmed_host'):
    """
    Preprocesses the input DataFrame for model training.
    This includes handling missing values, encoding categorical variables,
    and selecting relevant features.

    Parameters:
    - df: pandas DataFrame containing the raw data
    - target_column: name of the supervised training target column

    Returns:
    - X: Features (numpy array)
    - y: Target variable (numpy array)
    """

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if df.empty:
        raise ValueError("No rows were returned for training.")

    df = df.copy()

    if target_column not in df.columns:
        logger.log_warning(
            f"Training data does not include '{target_column}'. "
            "Using a synthetic positive label for all rows."
        )
        df[target_column] = 1

    df = df.dropna(subset=[target_column])
    if df.empty:
        raise ValueError("No training rows remain after removing missing target values.")

    feature_df = df.drop(columns=[target_column])
    numeric_features = feature_df.apply(pd.to_numeric, errors='coerce')
    numeric_features = numeric_features.dropna(axis=1, how='all')

    if numeric_features.empty:
        raise ValueError("No numeric feature columns are available for training.")

    numeric_features = numeric_features.fillna(numeric_features.median(numeric_only=True))
    y = pd.to_numeric(df[target_column], errors='coerce').fillna(0).to_numpy()
    X = numeric_features.to_numpy()
    
    return X, y