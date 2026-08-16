# A unit test module for the preprocessor functions in the gaiaml package.

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

import src.preprocessing.preprocessor as preprocessor
from src.preprocessing.preprocessor import (
    preprocess_gaia_data,
    preprocess_confirmed_exoplanets_data,
)
from src.training import xgboost_trainer
from data.database.sqlite import db as database_db


def test_preprocess_gaia_data_uses_negative_label_for_unlabeled_rows():
    df = pd.DataFrame({
        "ra": [1.0],
        "dec": [2.0],
        "parallax": [3.0],
    })

    X, y = preprocess_gaia_data(df)

    assert X.shape == (1, 3)
    assert y[0] == 0


def test_preprocess_confirmed_exoplanets_data_uses_positive_label_for_confirmed_rows():
    df = pd.DataFrame({
        "ra": [1.0],
        "dec": [2.0],
        "parallax": [3.0],
    })

    X, y = preprocess_confirmed_exoplanets_data(df)

    assert X.shape == (1, 3)
    assert y[0] == 1


def test_ensure_training_data_available_downloads_missing_sources(monkeypatch):
    calls = []
    fetch_counts = {"gaia_dr3_data": 0, "confirmed_exoplanets_data": 0}

    def fake_fetch_data(table_name, limit=-1, as_dataframe=False):
        if table_name == "gaia_dr3_data":
            fetch_counts[table_name] += 1
            if fetch_counts[table_name] == 1:
                return pd.DataFrame()
            return pd.DataFrame({"source_id": [1], "ra": [1.0]})
        if table_name == "confirmed_exoplanets_data":
            fetch_counts[table_name] += 1
            if fetch_counts[table_name] == 1:
                return pd.DataFrame()
            return pd.DataFrame({"source_id": [2], "ra": [2.0]})
        raise AssertionError(f"Unexpected table: {table_name}")

    def fake_download_gaia(*args, **kwargs):
        calls.append(("gaia", kwargs.get("count"), kwargs.get("force_refresh", False)))

    def fake_download_confirmed(*args, **kwargs):
        calls.append(("confirmed", kwargs.get("count"), kwargs.get("force_refresh", False)))

    monkeypatch.setattr(preprocessor.db, "fetch_data", fake_fetch_data)
    monkeypatch.setattr(preprocessor, "gaia_downloader", type("Dummy", (), {"download_gaia_dr3_data": fake_download_gaia, "download_confirmed_exoplanets_data": fake_download_confirmed})())

    gaia_df, confirmed_df = preprocessor.ensure_training_data_available(gaia_rows=5, confirmed_rows=3)

    assert calls == [("gaia", 5, True), ("confirmed", 3, True)]
    assert not gaia_df.empty
    assert not confirmed_df.empty


def test_create_training_dataset_includes_reinforcement_examples(monkeypatch):
    gaia_df = pd.DataFrame({"source_id": [1], "ra": [1.0], "dec": [2.0]})
    confirmed_df = pd.DataFrame({"source_id": [2], "ra": [3.0], "dec": [4.0]})
    reinforcement_df = pd.DataFrame({
        "source_id": [3],
        "is_confirmed_host": [1],
        "prediction": [0.9],
    })

    monkeypatch.setattr(preprocessor, "ensure_training_data_available", lambda: (gaia_df, confirmed_df))

    def fake_fetch_data(table_name, limit=-1, as_dataframe=False):
        if table_name == "reinforcement_examples":
            return reinforcement_df
        if table_name == "test_data":
            return pd.DataFrame()
        raise AssertionError(f"Unexpected table: {table_name}")

    monkeypatch.setattr(preprocessor.db, "fetch_data", fake_fetch_data)

    X, y = preprocessor.create_training_dataset_from_gaia_dr3()

    assert X.shape[0] >= 2
    assert y.tolist()[-1] == 1


def test_evaluate_binary_metrics_returns_expected_scores():
    metrics = xgboost_trainer.evaluate_binary_metrics([1, 0, 1, 1], [1, 0, 0, 1])

    assert metrics["accuracy"] == 0.75
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 2 / 3


def test_run_reinforcement_training_loop_stops_when_target_reached(monkeypatch):
    calls = []

    def fake_train(iteration):
        calls.append(iteration)
        return {"iteration": iteration}

    def fake_evaluate(train_result, iteration):
        return {"accuracy": 1.0 if iteration == 1 else 0.0, "precision": 1.0, "recall": 1.0}

    result = xgboost_trainer.run_reinforcement_training_loop(
        fake_train,
        fake_evaluate,
        max_iterations=3,
        target_accuracy=0.99,
        target_precision=0.99,
    )

    assert result["achieved"] is True
    assert len(result["history"]) == 1
    assert calls == [1]


def test_get_latest_model_metrics_returns_latest_saved_metrics(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database_db, "_get_database_path", lambda: str(db_path))

    database_db.initialize_database()
    database_db.save_model_version_json(
        version="0.0.1",
        date_created="2024-01-01",
        f1=0.90,
        accuracy=0.88,
        precision=0.92,
        recall=0.87,
        model_json="/tmp/model_v0_0_1.json",
    )
    database_db.save_model_version_json(
        version="0.0.2",
        date_created="2024-01-02",
        f1=0.95,
        accuracy=0.94,
        precision=0.96,
        recall=0.93,
        model_json="/tmp/model_v0_0_2.json",
    )

    metrics = database_db.get_latest_model_metrics()

    assert metrics is not None
    assert metrics["version"] == "0.0.2"
    assert metrics["accuracy"] == 0.94
    assert metrics["precision"] == 0.96
    assert metrics["recall"] == 0.93
    assert metrics["f1"] == 0.95


def test_store_predictions_replaces_existing_rows(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database_db, "_get_database_path", lambda: str(db_path))

    database_db.initialize_database()
    database_db.store_predictions(
        "new_exoplanet_candidates",
        pd.DataFrame({"source_id": [1], "likelihood": [0.9]}),
        replace_existing=True,
    )
    database_db.store_predictions(
        "new_exoplanet_candidates",
        pd.DataFrame({"source_id": [2], "likelihood": [0.2]}),
        replace_existing=True,
    )

    rows = database_db.fetch_data("new_exoplanet_candidates", -1, as_dataframe=True)

    assert rows["source_id"].tolist() == [2]
    assert rows["likelihood"].tolist() == [0.2]
