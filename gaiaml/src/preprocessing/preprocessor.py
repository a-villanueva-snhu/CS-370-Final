## Preprocesses raw Gaia Data into a format suitable for 
# machine learning models. This includes cleaning, 
# normalization, and feature engineering.

import pandas as pd
from data.database.sqlite import db as db
import logs.logger as logger


## -- Preprocess Gaia Data -- ##
## Feature Selection and Preprocessing ##
# TODO: edit to include feature engineering, normalization, and other preprocessing steps as needed.
# FIXME: target column needs to only be included in the confirmed exoplanets data, not the Gaia DR3 data. 
#   The Gaia DR3 data is unlabeled and should not have a target column. 
#   The target column should be added to the confirmed exoplanets data 
#   for supervised training.
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
    # If we are preprocessing confirmed exoplanets data, we may not have the target column. In that case, we can create a synthetic target column.
    if target_column not in df.columns:
        logger.log_warning(
            f"Training data does not include '{target_column}'. "
            "Using a synthetic positive label for all rows."
        )
        df[target_column] = 1


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

    ## Feature Selection and Preprocessing ##
    # Drop non-numeric columns and handle missing values
    feature_df = df.drop(columns=[target_column])
    numeric_features = feature_df.apply(pd.to_numeric, errors='coerce')
    numeric_features = numeric_features.dropna(axis=1, how='all')

    # Handle missing values by filling with median
    numeric_features = numeric_features.fillna(numeric_features.median(numeric_only=True))
    if numeric_features.empty:
        raise ValueError("No numeric feature columns are available for training.")

    # Convert target column to numeric and fill missing values with 0
    numeric_features = numeric_features.fillna(numeric_features.median(numeric_only=True))
    y = pd.to_numeric(df[target_column], errors='coerce').fillna(0).to_numpy()
    X = numeric_features.to_numpy()
    
    return X, y


def preprocess_confirmed_exoplanets_data(df, target_column='is_confirmed_host'):
    """
    Preprocesses the confirmed exoplanets data for model training.
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

    ## Feature Selection and Preprocessing ##
    # Drop non-numeric columns and handle missing values
    feature_df = df.drop(columns=[target_column])
    numeric_features = feature_df.apply(pd.to_numeric, errors='coerce')
    numeric_features = numeric_features.dropna(axis=1, how='all')

    # Handle missing values by filling with median
    numeric_features = numeric_features.fillna(numeric_features.median(numeric_only=True))
    if numeric_features.empty:
        raise ValueError("No numeric feature columns are available for training.")

    # Convert target column to numeric and fill missing values with 0
    y = pd.to_numeric(df[target_column], errors='coerce').fillna(0).to_numpy()
    X = numeric_features.to_numpy()
    
    return X, y

def create_training_dataset_from_gaia_dr3():
    """
    Creates a training dataset from the Gaia DR3 data.
    This function fetches the Gaia DR3 data from the database,
    preprocesses it, and returns the features and target variable,
    which also insures that the set includes some confirmed exoplanets data for supervised training.

    Returns:
    - X: Features (numpy array)
    - y: Target variable (numpy array)
    """
    # Fetch Gaia DR3 data from the database
    df = db.fetch_data("gaia_dr3_data", -1, as_dataframe=True)
    if df.empty:
        logger.log_warning("gaia_dr3_data is empty. Falling back to test_data for preprocessing.")
        df = db.fetch_data("test_data", -1, as_dataframe=True)

    # Preprocess the Gaia DR3 data
    X_gaia, y_gaia = preprocess_gaia_data(df)

    # Fetch confirmed exoplanets data from the database
    df_confirmed = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)
    if df_confirmed.empty:
        logger.log_warning("confirmed_exoplanets_data is empty. No confirmed exoplanets data available for training.")
        return X_gaia, y_gaia

    # Preprocess the confirmed exoplanets data
    X_confirmed, y_confirmed = preprocess_confirmed_exoplanets_data(df_confirmed)

    # Combine the Gaia DR3 and confirmed exoplanets datasets
    X_combined = pd.concat([pd.DataFrame(X_gaia), pd.DataFrame(X_confirmed)], ignore_index=True).to_numpy()
    y_combined = pd.concat([pd.Series(y_gaia), pd.Series(y_confirmed)], ignore_index=True).to_numpy()

    return X_combined, y_combined