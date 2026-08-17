## Takes in training data and trains an XGBoost model on it. 
# It is used by the other files in the project to train the 
# model for later predictions.
# It is also used to save and load the model from the 
# versioning database.

import datetime
import os

from data.database.sqlite import db as db
import xgboost as xgb
import numpy as np
# import pandas as pd
from sklearn.model_selection import train_test_split
from config import config_manager
import logs.logger as logger


def _can_use_stratify(y, test_size):
    """Return whether train_test_split can safely stratify this binary target."""
    y = np.asarray(y)
    if y.size < 2:
        return False
    unique_values, counts = np.unique(y, return_counts=True)
    if len(unique_values) < 2:
        return False

    # Stratified splitting requires at least one sample from each class in test/train.
    if isinstance(test_size, float):
        test_count = int(np.ceil(y.size * test_size))
    else:
        test_count = int(test_size)
    train_count = int(y.size - test_count)
    if test_count < len(unique_values) or train_count < len(unique_values):
        return False
    return bool(np.all(counts >= 2))


def evaluate_binary_metrics(y_true, y_pred):
    """Return accuracy, precision, recall, and F1 for binary predictions."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    # Precision/recall/F1 are not meaningful when the validation labels contain only one class.
    unique_classes = np.unique(y_true)
    has_both_classes = len(unique_classes) == 2 and set(unique_classes).issubset({0, 1})

    if has_both_classes:
        precision = float(precision_score(y_true, y_pred, zero_division=0))
        recall = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
    else:
        precision = float("nan")
        recall = float("nan")
        f1 = float("nan")

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "binary_eval_valid": has_both_classes,
    }


def select_decision_threshold(y_true, y_score, default_threshold=0.5):
    """Choose a binary decision threshold that maximizes F1 on the provided labels/scores."""
    from sklearn.metrics import precision_recall_curve

    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    unique_classes = np.unique(y_true)
    has_both_classes = len(unique_classes) == 2 and set(unique_classes).issubset({0, 1})
    if not has_both_classes:
        return float(default_threshold)

    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    if thresholds.size == 0:
        return float(default_threshold)

    # precision/recall are one element longer than thresholds.
    f1_scores = (2 * precision[:-1] * recall[:-1]) / np.clip(precision[:-1] + recall[:-1], 1e-12, None)
    best_index = int(np.nanargmax(f1_scores))
    best_threshold = float(thresholds[best_index])

    # Keep threshold in a sane probability range.
    return float(np.clip(best_threshold, 0.05, 0.95))


def run_reinforcement_training_loop(
    train_fn,
    evaluate_fn,
    max_iterations=config_manager.get_config_val_as_int('reinforcement_training.max_iterations', 25),
    target_accuracy=config_manager.get_config_value_as_float('reinforcement_training.target_accuracy', 0.99),
    target_precision=config_manager.get_config_value_as_float('reinforcement_training.target_precision', 0.99),
    target_recall=config_manager.get_config_value_as_float('reinforcement_training.target_recall', 0.99),
):
    """Iterate training and evaluation until a target quality level is reached."""
    history = []
    achieved = False
    start_time = datetime.datetime.now()

    for iteration in range(1, int(max_iterations) + 1):
        last_time = datetime.datetime.now()
        train_result = train_fn(iteration)
        metrics = evaluate_fn(train_result, iteration)
        history.append({"iteration": iteration, **metrics})

        # log time for this iteration
        iteration_time = datetime.datetime.now() - last_time
        logger.log_info(f"Iteration {iteration} completed in {iteration_time.total_seconds():.2f} seconds. Metrics: {metrics}")

        if (
            metrics.get("accuracy", 0.0) >= target_accuracy
            and metrics.get("precision", 0.0) >= target_precision
            and metrics.get("recall", 0.0) >= target_recall
        ):
            achieved = True
            break

    return {"achieved": achieved, "history": history}


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
    stratify = y if _can_use_stratify(y, test_size) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    # Create an internal validation split from the training fold for threshold calibration.
    val_size = 0.25
    stratify_train = y_train if _can_use_stratify(y_train, val_size) else None
    X_fit = X_train
    y_fit = y_train
    X_val = None
    y_val = None
    if len(X_train) >= 8:
        try:
            X_fit, X_val, y_fit, y_val = train_test_split(
                X_train,
                y_train,
                test_size=val_size,
                random_state=random_state,
                stratify=stratify_train,
            )
        except ValueError:
            X_fit = X_train
            y_fit = y_train
            X_val = None
            y_val = None

    # Create an XGBoost DMatrix for training
    dtrain = xgb.DMatrix(X_fit, label=y_fit)
    
    # Set default parameters if none are provided
    if model_params is None:
        unique_targets = np.unique(y_fit)
        is_binary_classification = len(unique_targets) == 2 and set(unique_targets).issubset({0, 1})

        positive_count = int(np.sum(y_fit == 1))
        negative_count = int(np.sum(y_fit == 0))
        scale_pos_weight = (negative_count / positive_count) if positive_count else 1.0

        model_params = {
            'objective': 'binary:logistic' if is_binary_classification else 'reg:squarederror',
            'eval_metric': 'logloss' if is_binary_classification else 'rmse',
            'max_depth': 4,
            'eta': 0.2,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'seed': random_state,
            'scale_pos_weight': scale_pos_weight,
            'min_child_weight': 2,
            'gamma': 0.1,
        }

    # Train the model
    # TODO: Consider adding early stopping rounds and evaluation sets for better training control
    # TODO: Consider adding tree-weighted cross-validation for hyperparameter tuning
    model = xgb.train(model_params, dtrain)

    ## Predictions for internal validation (optional)
    dtest = xgb.DMatrix(X_test)

    # Evaluate on the untouched test fold; threshold is calibrated on validation fold only.
    y_pred = model.predict(dtest)
    decision_threshold = 0.5
    if 'binary:logistic' in model_params['objective']:
        if X_val is not None and y_val is not None and len(np.unique(np.asarray(y_val).astype(int))) == 2:
            y_val_pred = model.predict(xgb.DMatrix(X_val))
            decision_threshold = select_decision_threshold(y_val, y_val_pred, default_threshold=0.5)
        else:
            logger.log_warning(
                "Validation split for threshold calibration is unavailable or single-class. "
                "Using default decision threshold 0.5."
            )
    y_pred_binary = (y_pred >= decision_threshold).astype(int) if 'binary:logistic' in model_params['objective'] else y_pred

    # Calculate internal validation metrics if needed
    if 'binary:logistic' in model_params['objective']:
        metrics = evaluate_binary_metrics(y_test, y_pred_binary)
        if not metrics.get("binary_eval_valid", False):
            logger.log_warning(
                "Internal validation labels contain only one class in y_test. "
                "Precision/recall/F1 are recorded as NaN to avoid misleading perfect metrics."
            )
            decision_threshold = 0.5
        f1 = metrics["f1"]
        accuracy = metrics["accuracy"]
        precision = metrics["precision"]
        recall = metrics["recall"]
        logger.log_info(
            f"Internal validation threshold={decision_threshold:.3f} accuracy={accuracy:.4f} "
            f"precision={precision:.4f} recall={recall:.4f} f1={f1:.4f}"
        )
        model.set_attr(decision_threshold=f"{max(0.05, decision_threshold - 1e-9):.12f}")
    else:
        f1 = accuracy = precision = recall = None


    # Export to JSON for the database versioning system
    model_version = config_manager.get_next_model_version()

    # formatted model version string for json filename export
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    model_dir = os.path.join(project_root, 'gaiaml', 'src', 'models')
    jstring = os.path.join(model_dir, f"xgboost_model_v{model_version.replace('.', '_')}.json")

    # check that the directory exists
    try:
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    except Exception as e:
        logger.log_error(f"Failed to create directory for model JSON: {e}")
        raise

    # Save the model to a JSON file
    model.save_model(jstring)  # Save the model to a JSON file

    
    db.save_model_version_json(
        version=model_version,
        date_created=config_manager.get_current_date(),
        f1=f1,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        model_json=jstring
    )

    return model, X_test, y_test