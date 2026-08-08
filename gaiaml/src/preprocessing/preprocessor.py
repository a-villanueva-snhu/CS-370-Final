## Preprocesses raw Gaia Data into a format suitable for 
# machine learning models. This includes cleaning, 
# normalization, and feature engineering.

import numpy as np
import pandas as pd
from data.database.sqlite import db as db
import logs.logger as logger
from src.utils import gaia_downloader


def _select_numeric_features(df, target_column):
    """Return a numeric feature DataFrame for model training."""
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    feature_df = df.drop(columns=[target_column], errors="ignore")
    numeric_features = feature_df.apply(pd.to_numeric, errors="coerce")
    numeric_features = numeric_features.dropna(axis=1, how="all")
    numeric_features = numeric_features.fillna(numeric_features.median(numeric_only=True))
    return numeric_features


def ensure_training_data_available(gaia_rows=100, confirmed_rows=10):
    """Ensure Gaia DR3 and confirmed-exoplanet training data exist by using the existing downloader flow."""

    gaia_df = db.fetch_data("gaia_dr3_data", -1, as_dataframe=True)
    if gaia_df.empty:
        logger.log_info("gaia_dr3_data is empty. Downloading Gaia DR3 data via the existing downloader.")
        gaia_downloader.download_gaia_dr3_data(count=gaia_rows, force_refresh=True)
        gaia_df = db.fetch_data("gaia_dr3_data", -1, as_dataframe=True)

    confirmed_df = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)
    if confirmed_df.empty:
        logger.log_info("confirmed_exoplanets_data is empty. Downloading confirmed exoplanet data via the existing downloader.")
        gaia_downloader.download_confirmed_exoplanets_data(count=confirmed_rows, force_refresh=True)
        confirmed_df = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)

    return gaia_df, confirmed_df


## -- Preprocess Gaia Data -- ##
## Feature Selection and Preprocessing ##
# TODO: edit to include feature engineering, normalization, and other preprocessing steps as needed.
# FIXME: target column needs to only be included in the confirmed exoplanets data, not the Gaia DR3 data. 
#   The Gaia DR3 data is unlabeled and should not have a target column. 
#   The target column should be added to the confirmed exoplanets data 
#   for supervised training.
def preprocess_gaia_data(df, target_column='is_confirmed_host', default_target=0):
    """
    Preprocesses the input DataFrame for model training.
    This includes handling missing values, encoding categorical variables,
    and selecting relevant features.

    Parameters:
    - df: pandas DataFrame containing the raw data
    - target_column: name of the supervised training target column
    - default_target: label to assign when the target column is missing

    Returns:
    - X: Features (numpy array)
    - y: Target variable (numpy array)
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    df = df.copy()

    if target_column not in df.columns:
        logger.log_info(
            f"Training data does not include '{target_column}'. Assigning a binary label of {default_target} for all rows."
        )
        df[target_column] = default_target


    if df.empty:
        raise ValueError("No rows were returned for training.")

    df = df.copy()

    if target_column not in df.columns:
        logger.log_info(
            f"Training data does not include '{target_column}'. Assigning a binary label of {default_target} for all rows."
        )
        df[target_column] = default_target

    df = df.dropna(subset=[target_column])
    if df.empty:
        raise ValueError("No training rows remain after removing missing target values.")

    ## Feature Selection and Preprocessing ##
    numeric_features = _select_numeric_features(df, target_column)
    if numeric_features.empty:
        raise ValueError("No numeric feature columns are available for training.")

    # Convert target column to numeric and fill missing values with 0
    y = pd.to_numeric(df[target_column], errors='coerce').fillna(0).to_numpy()
    X = numeric_features.to_numpy()
    
    return X, y


def preprocess_confirmed_exoplanets_data(df, target_column='is_confirmed_host', default_target=1):
    """
    Preprocesses the confirmed exoplanets data for model training.
    This includes handling missing values, encoding categorical variables,
    and selecting relevant features.

    Parameters:
    - df: pandas DataFrame containing the raw data
    - target_column: name of the supervised training target column
    - default_target: label to assign when the target column is missing

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
        logger.log_info(
            f"Training data does not include '{target_column}'. Assigning a binary label of {default_target} for all rows."
        )
        df[target_column] = default_target

    df = df.dropna(subset=[target_column])
    if df.empty:
        raise ValueError("No training rows remain after removing missing target values.")

    ## Feature Selection and Preprocessing ##
    numeric_features = _select_numeric_features(df, target_column)
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
    # Ensure the required training sources exist by using the existing downloader workflow.
    df, df_confirmed = ensure_training_data_available()

    reinforcement_df = db.fetch_data("reinforcement_examples", -1, as_dataframe=True)
    if not reinforcement_df.empty and "source_id" in reinforcement_df.columns:
        reinforcement_df = reinforcement_df.copy()
        reinforcement_df["is_confirmed_host"] = reinforcement_df["is_confirmed_host"].astype(int)
        reinforcement_df["prediction"] = pd.to_numeric(reinforcement_df["prediction"], errors="coerce")
        reinforcement_df = reinforcement_df.dropna(subset=["prediction"])

    if df.empty:
        logger.log_warning("gaia_dr3_data is empty after download attempt. Falling back to test_data for preprocessing.")
        df = db.fetch_data("test_data", -1, as_dataframe=True)

    if "is_confirmed_host" not in df.columns:
        df = df.copy()
        df["is_confirmed_host"] = 0

    if df_confirmed is not None and "is_confirmed_host" not in df_confirmed.columns:
        df_confirmed = df_confirmed.copy()
        df_confirmed["is_confirmed_host"] = 1

    # Preprocess the Gaia DR3 data as unlabeled negatives for training.
    X_gaia, y_gaia = preprocess_gaia_data(df, target_column='is_confirmed_host', default_target=0)

    if df_confirmed.empty:
        logger.log_warning("confirmed_exoplanets_data is empty after download attempt. No confirmed exoplanets data available for training.")
        return X_gaia, y_gaia

    # Preprocess the confirmed exoplanets data as positive examples.
    X_confirmed, y_confirmed = preprocess_confirmed_exoplanets_data(df_confirmed, target_column='is_confirmed_host', default_target=1)

    # Combine the Gaia DR3 and confirmed exoplanets datasets
    X_combined = pd.concat([pd.DataFrame(X_gaia), pd.DataFrame(X_confirmed)], ignore_index=True).to_numpy()
    y_combined = pd.concat([pd.Series(y_gaia), pd.Series(y_confirmed)], ignore_index=True).to_numpy()

    if not reinforcement_df.empty:
        reinforcement_labels = reinforcement_df["is_confirmed_host"].astype(int).to_numpy()
        gaia_feature_frame = df[["source_id"] + [col for col in ["ra", "dec", "parallax", "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag"] if col in df.columns]].copy()
        if not gaia_feature_frame.empty and "source_id" in gaia_feature_frame.columns:
            reinforcement_joined = reinforcement_df[["source_id", "is_confirmed_host", "prediction"]].copy()
            reinforcement_joined = reinforcement_joined.merge(
                gaia_feature_frame,
                on="source_id",
                how="left",
            )
            reinforcement_joined = reinforcement_joined.dropna(subset=[col for col in ["ra", "dec", "parallax", "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag"] if col in reinforcement_joined.columns])
            if not reinforcement_joined.empty:
                feature_columns = [col for col in ["ra", "dec", "parallax", "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag"] if col in reinforcement_joined.columns]
                reinforcement_features = reinforcement_joined[feature_columns].astype(float).to_numpy()
                if reinforcement_features.shape[1] == X_combined.shape[1]:
                    X_combined = np.vstack([X_combined, reinforcement_features])
                    y_combined = np.concatenate([y_combined, reinforcement_joined["is_confirmed_host"].astype(int).to_numpy()])

    return X_combined, y_combined