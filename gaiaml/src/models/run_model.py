## The Core model for the GaiaML project. 
# Takes a trained model and uses it to make predictions on new data.
# It is used by the other files in the project to make predictions on new data.


import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from data.database.sqlite import db as db
from config import config_manager
import logs.logger as logger
from datetime import datetime

def run_model():
    """
    Pulls the trained model from the versioning database and uses it to make predictions on new data.
    """
    logger.log_info("Running the trained model on new data...")
    # Prefer explicit config version, otherwise use latest model version in DB.
    model_version = config_manager.get_config_value("model_version", default=None)
    if not isinstance(model_version, str) or not model_version:
        model_version = db.get_latest_model_version()
    if not model_version:
        raise ValueError("No model version available for deployment. Train a model first.")

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
    prediction_features = rd.drop(columns=["source_id"], errors="ignore")
    s_prediction: np.ndarray = model.predict(xgb.DMatrix(prediction_features))

    # Store prediction rows with source IDs for traceability.
    pred_df = pd.DataFrame({
        "source_id": rd["source_id"].to_numpy() if "source_id" in rd.columns else np.arange(len(s_prediction)),
        "prediction": s_prediction,
    })
    db.store_predictions("predictions", pred_df)

    # TODO: Split this into the cross_checker module

    # Include checking against known hosts
    known_hosts: pd.DataFrame = db.fetch_data("confirmed_exoplanets_data", as_dataframe=True)
    if not known_hosts.empty:
        # Check for matches between predictions and known hosts
        matches = rd[rd["source_id"].isin(known_hosts["source_id"])]
        if not matches.empty:
            logger.log_info(f"Found {len(matches)} matches between predictions and known hosts.")

    # weigh the predictions against the known hosts to see if the model is performing well
    if not known_hosts.empty:
        # Merge predictions with known hosts to evaluate performance
        merged = pd.merge(rd, known_hosts, on="source_id", how="inner")
        if not merged.empty:
            y_true = merged["is_confirmed_host_y"].to_numpy()  # True labels from known hosts
            y_pred = model.predict(xgb.DMatrix(merged.drop(columns=["source_id", "is_confirmed_host_y"])))
            # Evaluate the model's performance using metrics like accuracy, precision, recall, etc.
            from sklearn.metrics import accuracy_score, precision_score, recall_score
            accuracy = accuracy_score(y_true, (y_pred > 0.5).astype(int))
            precision = precision_score(y_true, (y_pred > 0.5).astype(int), zero_division=0)
            recall = recall_score(y_true, (y_pred > 0.5).astype(int), zero_division=0)
            logger.log_info(f"Model Evaluation - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")

            reinforcement_df = pd.DataFrame({
                "source_id": merged["source_id"].to_numpy(),
                "is_confirmed_host": merged["is_confirmed_host_y"].to_numpy(),
                "prediction": y_pred,
            })
            db.append_reinforcement_examples(reinforcement_df)
            logger.log_info(f"Stored {len(reinforcement_df)} reinforcement examples for future training.")
        else:
            logger.log_warning("No overlapping source_ids found between predictions and known hosts for evaluation.")

    # determine likelihood of new exoplanet candidates based on the model's predictions
    new_candidates: pd.DataFrame = rd[~rd["source_id"].isin(known_hosts["source_id"])]
    if not new_candidates.empty:
        new_candidate_features = new_candidates.drop(columns=["source_id"], errors="ignore")
        new_candidates = new_candidates.copy()
        new_candidates["likelihood"] = model.predict(xgb.DMatrix(new_candidate_features))
        db.store_predictions("new_exoplanet_candidates", new_candidates[["source_id", "likelihood"]])

    # Save the model to the versioning database

    
    
    

