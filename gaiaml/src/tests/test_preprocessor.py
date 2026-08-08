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
