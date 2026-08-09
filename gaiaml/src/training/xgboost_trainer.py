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
import logs.logger as logger


def evaluate_binary_metrics(y_true, y_pred):
    """Return accuracy, precision, recall, and F1 for binary predictions."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def run_reinforcement_training_loop(
    train_fn,
    evaluate_fn,
    max_iterations=5,
    target_accuracy=0.99,
    target_precision=0.99,
    target_recall=0.99,
):
    """Iterate training and evaluation until a target quality level is reached."""
    history = []
    achieved = False

    for iteration in range(1, max_iterations + 1):
        train_result = train_fn(iteration)
        metrics = evaluate_fn(train_result, iteration)
        history.append({"iteration": iteration, **metrics})

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
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Create an XGBoost DMatrix for training
    dtrain = xgb.DMatrix(X_train, label=y_train)
    
    # Set default parameters if none are provided
    if model_params is None:
        unique_targets = np.unique(y_train)
        is_binary_classification = len(unique_targets) == 2 and set(unique_targets).issubset({0, 1})

        positive_count = int(np.sum(y_train == 1))
        negative_count = int(np.sum(y_train == 0))
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

    # F1 Score, Accuracy, Precision, Recall can be calculated here if needed for internal validation
    y_pred = model.predict(dtest)
    y_pred_binary = (y_pred > 0.3).astype(int) if 'binary:logistic' in model_params['objective'] else y_pred

    # Calculate internal validation metrics if needed
    if 'binary:logistic' in model_params['objective']:
        metrics = evaluate_binary_metrics(y_test, y_pred_binary)
        f1 = metrics["f1"]
        accuracy = metrics["accuracy"]
        precision = metrics["precision"]
        recall = metrics["recall"]
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