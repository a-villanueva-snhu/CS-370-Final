# CS-499 Capstone Project
Final Project for SNHU CS-499
Aiden Villanueva
July 20, 2026

Version:

1.2.0     |     Updated Gaia data downloader and confirmed exoplanet downloader
          |     Added typed database fetch behavior and stricter config/database path handling
          |     Expanded CLI workflow (download confirmed exoplanets, config editing, table regeneration)
          |     Updated training and preprocessing pipeline documentation

1.1.0     |     Added User Guide, Developer Guide,       
          |         Installation and Configuration sections
          |     Added Testing and Model Management descriptions

1.0.0     |     Added basic description and module breakdown


# Project GaiaML
Project GaiaML is an open-source scientific data tool designed to use eXtreme Gradient Boosted (XGBoost) trees in order to classify Gaia DR3 data against NASA's Exoplanet Archive of known and suspected exoplanet host stars. 

The goal is to show that XGBoost is a strong choice for analyzing large, tabularized data sets such as many astronomical data, and that it is capable of being tuned and trained to accurately classify known systems as well as to create predictions for possible new candidates. 

Current implementation status: the pipeline can download Gaia DR3 rows, preprocess data, train an XGBoost model, and save model versions and metrics. The current training fallback behavior can synthesize a positive target label when no explicit supervised target column exists.

# Project Structure

The project is organized around data preparation, model training, evaluation, and prediction. Key folders and files are arranged to separate data ingestion, feature engineering, training pipelines, and results.

- config/: YAML file(s) for globalizing variables and model configuration parameters.
- data/: raw data files, cleaned datasets, and lookup tables.
- src/: core project code including data processing, feature engineering, and model utilities.
- docs/: supplementary documentation, notes, and reference material.

# Main Files

- `main.py`: entry point for running the training and prediction workflow.
- `gaia_downloader.py`: handles Gaia DR3 download and confirmed exoplanet sample download.
- `preprocessor.py`: handles numeric feature filtering, missing value handling, and target preparation.
- `xgboost_trainer.py`: trains XGBoost, computes optional validation metrics, saves model JSON, and records model versions.
- `model_evaluator.py`: evaluates model performance on test data and generates metrics.
- `model.py`: runs the trained model on new Gaia DR3 data for candidate classification.

Deprecated artifacts such as `TreasureHuntGame`, `TreasureMaze.py`, and `GameExperience.py` are intentionally excluded from the final project structure and documentation.

# CLI Flowchart
The core of GaiaML is a command-line interface which uses a menu as a state machine 
to match user input strings to functional modules. 

![CLI Flowchart](gaiaml/embeds/gaiaml_corepipeline.drawio.png)


# Installation
Prerequisites:
- Python 3.8 or higher
- pip (Python package manager)

Required packages:
- xgboost
- pandas
- numpy
- scikit-learn
- pyyaml
- requests
- astroquery

To install dependencies:
```bash
pip install -r requirements.txt
```

# User Guide

Run `main.py` to launch the program:
```bash
python main.py
```

The CLI supports the following core commands:
- `download`: download data from Gaia DR3 (`g`) or confirmed exoplanets (`c`)
- `preprocess`: preprocess Gaia and confirmed exoplanets datasets
- `train`: train the XGBoost model
- `config`: load/open/edit config values
- `settings regen`: regenerate a specific database table schema
- `logs`: open the logs folder
- `test`: run basic test routines

Follow the on-screen prompts to select your desired workflow.

Recommended run sequence:
1. `download` -> `g` (Gaia DR3)
2. `download` -> `c` (confirmed exoplanets)
3. `preprocess`
4. `train`

# Developer Guide

## Code Organization

All source code is located in the `src/` directory. Each module handles a specific phase of the data pipeline:

- **Data Ingestion**: `gaia_downloader.py` manages Gaia DR3 and confirmed exoplanet data pulls
- **Feature Engineering**: `preprocessor.py` implements scaling, normalization, and feature derivation
- **Model Training**: `xgboost_trainer.py` handles hyperparameter tuning and model serialization
- **Evaluation**: `model_evaluator.py` generates metrics and validation reports
- **Inference**: `model.py` applies trained models to new data

## Training System

The current training system is designed around a tabular pipeline:

1. Data source tables
- `gaia_dr3_data`: general Gaia DR3 features
- `confirmed_exoplanets_data`: positive-class examples used to enrich supervised training
- `test_data`: small fallback sample table used for quick checks

2. Preprocessing (`src/preprocessing/preprocessor.py`)
- Converts inputs to pandas DataFrames
- Selects numeric features and drops all-non-numeric columns
- Fills missing feature values with median values
- Uses target column `is_confirmed_host` when present
- If target is missing, adds a synthetic positive target label and logs a warning

3. Training (`src/training/xgboost_trainer.py`)
- Splits data into train/test using `train_test_split`
- Chooses objective automatically:
    - `binary:logistic` for binary labels `{0,1}`
    - `reg:squarederror` otherwise
- Trains with `xgb.train` on a DMatrix
- Computes optional internal metrics (F1, accuracy, precision, recall) for binary mode

4. Model versioning
- Saves trained model JSON under `gaiaml/src/models/` with versioned naming
- Stores metadata in SQLite `model_versioning` table:
    - version
    - date_created
    - f1
    - accuracy
    - precision
    - recall
    - model_json path

5. Current limitation
- If the training dataset does not include a true negative class, the model can train successfully but may not represent a reliable classifier. Add explicit labeled negatives for production-quality classification.

## Configuration

All configurable parameters should be defined in `config/config.yaml`. This includes:
- Data source URLs and API endpoints
- Feature lists and engineering parameters
- XGBoost hyperparameters
- Train/test split ratios
- Output paths and logging levels

Important currently used config keys:
- `database_settings.database_file_path`
- `logging.log_file_path`

## Testing

Unit tests are located in the `tests/` directory and follow the naming convention `test_*.py`. To run tests:

```bash
python -m pytest tests/ -v
```

OR 

Use "test" from the main menu of the CLI.

Add tests for:
- Data validation and cleaning logic
- Feature engineering transformations
- Model training and prediction workflows
- Configuration loading and validation

## Model Management

Trained models are saved as versioned JSON files under `gaiaml/src/models/`.

Model versions are also stored in SQLite (`model_versioning`) with metadata:
- Training date
- Training data size
- Performance metrics
- Feature set version
