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

def run_model(count: int = 100, force_refresh: bool = False):
    """
    Pulls the trained model from the versioning database and uses it to make predictions on new data.
    """
    # runtime counter for logging
    start_time = datetime.now()


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
    rd: pd.DataFrame = db.fetch_data("gaia_dr3_data", count, as_dataframe=True)  # Fetch all available Gaia rows
    if rd.empty:
        raise ValueError("gaia_dr3_data is empty. Download Gaia DR3 data before deployment.")
    if "source_id" not in rd.columns:
        raise ValueError("gaia_dr3_data must include a source_id column for prediction traceability.")

    # Run extreme gradient boosting model on the data
    if model_json is not None:
        model.load_model(model_json)  # Load the trained model
    else:
        raise ValueError(f"Failed to load model version {model_version} from versioning database")

    threshold_attr = model.attr("decision_threshold")
    try:
        decision_threshold = float(threshold_attr) if threshold_attr is not None else 0.5
    except (TypeError, ValueError):
        decision_threshold = 0.5
    decision_threshold = float(np.clip(decision_threshold, 0.05, 0.95)) - 1e-9
    logger.log_info(f"Using decision threshold {decision_threshold:.3f} for binary classification.")

    # make predictions on the new data
    prediction_features = rd.drop(columns=["source_id", "is_confirmed_host"], errors="ignore")
    s_prediction: np.ndarray = model.predict(xgb.DMatrix(prediction_features))
    predicted_positive_count = int(np.sum(s_prediction >= decision_threshold))
    logger.log_info(
        f"Predicted positives at threshold {decision_threshold:.3f}: "
        f"{predicted_positive_count}/{len(s_prediction)}"
    )

    # Log time for model loading and prediction
    load_time = datetime.now() - start_time
    logger.log_info(f"Model loading and prediction took {load_time.total_seconds():.2f} seconds.")

    # Store prediction rows with source IDs for traceability.
    pred_df = pd.DataFrame({
        "source_id": rd["source_id"].to_numpy() if "source_id" in rd.columns else np.arange(len(s_prediction)),
        "prediction": s_prediction,
    })
    db.store_predictions("predictions", pred_df, replace_existing=True)

    # TODO: Split this into the cross_checker module

    model_feature_columns = prediction_features.columns.tolist()

    # Include checking against known hosts
    known_hosts: pd.DataFrame = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)
    if not known_hosts.empty and "is_confirmed_host" not in known_hosts.columns:
        known_hosts = known_hosts.copy()
        known_hosts["is_confirmed_host"] = 1
    if not known_hosts.empty:
        # Check for matches between predictions and known hosts
        matches = rd[rd["source_id"].isin(known_hosts["source_id"])]
        if not matches.empty:
            logger.log_info(f"Found {len(matches)} matches between predictions and known hosts.")

    # Score confirmed hosts directly (when feature columns are available) to build reinforcement data.
    if not known_hosts.empty and "source_id" in known_hosts.columns:
        available_feature_columns = [col for col in model_feature_columns if col in known_hosts.columns]
        if len(available_feature_columns) == len(model_feature_columns):
            known_host_features = known_hosts[available_feature_columns].copy()
            known_host_features = known_host_features.apply(pd.to_numeric, errors="coerce")
            known_host_features = known_host_features.fillna(known_host_features.median(numeric_only=True))

            confirmed_scores = model.predict(xgb.DMatrix(known_host_features))
            reinforcement_df = pd.DataFrame({
                "source_id": known_hosts["source_id"].to_numpy(),
                "is_confirmed_host": np.ones(len(known_hosts), dtype=int),
                "prediction": confirmed_scores,
            })
            db.append_reinforcement_examples(reinforcement_df)
            logger.log_info(f"Stored {len(reinforcement_df)} confirmed-host reinforcement examples.")
        else:
            logger.log_warning(
                "Skipped confirmed-host reinforcement scoring because required feature columns are missing."
            )

    # Log time for reinforcement scoring
    reinforcement_time = datetime.now() - start_time - load_time
    logger.log_info(f"Reinforcement scoring took {reinforcement_time.total_seconds():.2f} seconds.")

    # Weigh overlap predictions against known hosts when overlap rows are present.
    if not known_hosts.empty and "source_id" in known_hosts.columns:
        # Merge predictions with known hosts to evaluate overlap when available.
        merged = pd.merge(rd, known_hosts[["source_id", "is_confirmed_host"]], on="source_id", how="inner")
        if not merged.empty:
            y_true = merged["is_confirmed_host"].to_numpy()  # True labels from known hosts
            overlap_features = merged.drop(columns=["source_id", "is_confirmed_host"], errors="ignore")
            y_pred = model.predict(xgb.DMatrix(overlap_features))
            unique_label_count = len(np.unique(y_true))
            if unique_label_count < 2:
                logger.log_warning(
                    "Skipped deployment-time precision/recall reporting because validation labels contain only one class. "
                    "This check currently uses confirmed hosts only and cannot provide a reliable binary evaluation."
                )
            else:
                # Evaluate the model's performance using metrics like accuracy, precision, recall, etc.
                from sklearn.metrics import accuracy_score, precision_score, recall_score

                accuracy = accuracy_score(y_true, (y_pred > 0.5).astype(int))
                precision = precision_score(y_true, (y_pred > 0.5).astype(int), zero_division=0)
                recall = recall_score(y_true, (y_pred > 0.5).astype(int), zero_division=0)
                logger.log_info(f"Model Evaluation - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")

        else:
            logger.log_warning("No overlapping source_ids found between predictions and known hosts for evaluation.")

    # Log time for overlap evaluation
    overlap_time = datetime.now() - start_time - load_time - reinforcement_time
    logger.log_info(f"Overlap evaluation took {overlap_time.total_seconds():.2f} seconds.")

    # determine likelihood of new exoplanet candidates based on the model's predictions
    known_ids = set(known_hosts["source_id"].tolist()) if not known_hosts.empty and "source_id" in known_hosts.columns else set()
    candidate_mask = ~rd["source_id"].isin(known_ids)
    new_candidates: pd.DataFrame = rd.loc[candidate_mask, ["source_id"]].copy()
    if not new_candidates.empty:
        # Reuse already computed full-run predictions to keep candidate scoring aligned.
        new_candidates["likelihood"] = s_prediction[candidate_mask.to_numpy()]
        db.store_predictions(
            "new_exoplanet_candidates",
            new_candidates[["source_id", "likelihood"]],
            replace_existing=True,
        )

        report_df = new_candidates[["source_id", "likelihood"]].copy()
        report_df = report_df.sort_values(by="likelihood", ascending=False)
        report_df["confidence"] = report_df["likelihood"].apply(
            lambda value: "high" if value >= decision_threshold else "medium" if value >= (decision_threshold * 0.8) else "low"
        )
        report_df = report_df.reset_index(drop=True)
        logger.log_info("Top candidate report:")
        for _, row in report_df.head(10).iterrows():
            logger.log_info(
                f"source_id={int(row['source_id'])} likelihood={float(row['likelihood']):.4f} confidence={row['confidence']}"
            )

    # log time for candidate scoring
    candidate_time = datetime.now() - start_time - load_time - reinforcement_time - overlap_time
    logger.log_info(f"Candidate scoring took {candidate_time.total_seconds():.2f} seconds.")

    # Save the model to the versioning database
    ## Dont do this here, the model is already saved during training. This is just for reference.

    
    
    

