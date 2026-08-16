# CS-499 Capstone Project
Final Project for SNHU CS-499
Aiden Villanueva
July 20, 2026

Version:

1.4.0     |     Fixed deployment inference to score all available Gaia rows instead of a partial default slice
          |     Added adaptive decision-threshold selection from validation data and persisted threshold metadata on model artifacts
          |     Updated reinforcement flow to score confirmed-host rows directly and deduplicate reinforcement examples by source_id
          |     Improved candidate confidence reporting to align with the learned deployment threshold

1.3.0     |     Added explicit binary labels for training data so Gaia rows are treated as negatives and confirmed exoplanet rows as positives
          |     Expanded the training loop to support reinforcement examples and reuse verified predictions in later training runs
          |     Added deployment and candidate-likelihood reporting, with ranked candidate persistence in SQLite
          |     Expanded CLI workflow with `deploy`, `automate-reinforce`, and `candidates` commands plus non-interactive execution support

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

Current implementation status: the pipeline can download Gaia DR3 rows and confirmed exoplanet samples, preprocess data with explicit binary labels, train an XGBoost model, deploy it to score the full available Gaia dataset, persist candidate likelihoods, and store reinforcement examples for future training cycles. The workflow now supports adaptive threshold selection for binary decisions, threshold-aware candidate confidence reporting, and automated reinforcement iterations from the CLI.

# Project Structure

The project is organized around data preparation, model training, evaluation, and prediction. Key folders and files are arranged to separate data ingestion, feature engineering, training pipelines, persistence, and reporting.

- `gaiaml/cli/`: command-line entry points and workflow orchestration.
- `gaiaml/config/`: YAML-backed configuration helpers and runtime settings.
- `gaiaml/data/`: local datasets, exported artifacts, preprocessed tables, and SQLite databases.
- `gaiaml/src/`: core project code including data processing, feature engineering, training, evaluation, and model inference.
- `gaiaml/logs/`: logging infrastructure for training, deployment, and runtime diagnostics.
- `gaiaml/docs/` and `gaiaml/embeds/`: supporting documentation, notes, and diagram assets.

# Main Modules and Responsibilities

- `gaiaml/main.py`: top-level entry point for launching the CLI workflow.
- `gaiaml/cli/cli.py`: central command dispatcher for download, preprocess, train, deploy, automate-reinforce, candidates, and configuration actions.
- `gaiaml/config/config_manager.py`: loads and updates YAML configuration values such as database paths, logging settings, and default workflow parameters.
- `gaiaml/src/utils/gaia_downloader.py`: downloads Gaia DR3 rows into the local data store for later preprocessing and training.
- `gaiaml/src/utils/nasa_downloader.py`: downloads or loads confirmed exoplanet reference data used as positive examples.
- `gaiaml/src/preprocessing/preprocessor.py`: creates a supervised training matrix from Gaia rows and confirmed exoplanet references, assigning explicit binary labels.
- `gaiaml/src/preprocessing/cross_checker.py`: supports cross-checking, validation, and consistency checks across data sources.
- `gaiaml/src/training/xgboost_trainer.py`: trains the XGBoost classifier, computes binary metrics, serializes model JSON artifacts, and records model version metadata.
- `gaiaml/src/models/run_model.py`: loads the latest trained model, scores the current dataset, writes predictions, stores candidate likelihoods, and records reinforcement examples.
- `gaiaml/src/evaluation/model_evaluator.py`: provides evaluation helpers for model quality and internal validation.
- `gaiaml/data/database/sqlite/db.py`: central SQLite persistence layer for raw source rows, model versions, predictions, candidate likelihoods, and reinforcement examples.
- `gaiaml/logs/logger.py` and `gaiaml/logs/runtime_logger.py`: logging utilities for runtime and pipeline events.

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
- `deploy`: run the trained model on the current dataset and persist candidate likelihoods
- `automate-reinforce`: run repeated training/evaluation cycles and stop when target metrics are reached
- `candidates`: view the top-ranked candidate likelihoods stored from deployment runs
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
5. `deploy`
6. `candidates`

# Developer Guide

## Code Organization

The project is divided into a small set of focused modules that mirror the lifecycle of the machine-learning workflow:

- **CLI orchestration**: `gaiaml/cli/cli.py` coordinates user-facing commands and routes them into the appropriate preprocessing, training, deployment, or reporting steps.
- **Configuration**: `gaiaml/config/config_manager.py` loads YAML values and exposes helpers for database paths, logging configuration, and runtime settings.
- **Data acquisition**: `gaiaml/src/utils/gaia_downloader.py` and `gaiaml/src/utils/nasa_downloader.py` populate the local data sources used by the pipeline.
- **Feature engineering and labeling**: `gaiaml/src/preprocessing/preprocessor.py` assembles a supervised training frame and assigns explicit labels for positive and negative examples.
- **Model training**: `gaiaml/src/training/xgboost_trainer.py` trains the XGBoost classifier, evaluates binary metrics, and writes versioned model JSON files.
- **Deployment and inference**: `gaiaml/src/models/run_model.py` loads the newest model, scores the current dataset, stores prediction outputs, and records candidate likelihoods.
- **Persistence**: `gaiaml/data/database/sqlite/db.py` stores source data, model metadata, prediction rows, candidate rows, and reinforcement examples.
- **Monitoring**: `gaiaml/logs/logger.py` and `gaiaml/logs/runtime_logger.py` capture structured runtime messages for debugging and auditing.

## Training System

The current training system is designed around a tabular pipeline that uses public astronomy data and a binary classification objective:

1. **Data source tables**
- `gaia_dr3_data`: general Gaia DR3 features used as the primary feature source
- `confirmed_exoplanets_data`: positive-class reference rows used to enrich supervised training
- `new_exoplanet_candidates`: ranked candidate rows generated after deployment
- `reinforcement_examples`: verified cases that can be merged back into future training runs

2. **Preprocessing** (`gaiaml/src/preprocessing/preprocessor.py`)
- Converts inputs into pandas DataFrames
- Selects numeric feature columns and drops non-numeric values that cannot be used by XGBoost
- Fills missing values using median-based imputation
- Uses an explicit binary target where Gaia rows are treated as negatives and confirmed exoplanet rows are treated as positives
- Allows reinforcement rows to be appended into future training datasets using stable `source_id` values

3. **Training** (`gaiaml/src/training/xgboost_trainer.py`)
- Splits data into train/test using `train_test_split`
- Uses a binary logistic objective for labels in `{0, 1}`
- Applies class weighting and selects a validation-driven decision threshold to maximize binary classification utility
- Computes internal metrics such as accuracy, precision, recall, and F1 for the binary case
- Persists the learned decision threshold in model metadata for deployment-time reuse

4. **Model versioning**
- Saves trained model JSON under `gaiaml/src/models/` with versioned naming
- Stores metadata in SQLite `model_versioning` table:
    - version
    - date_created
    - f1
    - accuracy
    - precision
    - recall
    - model_json path

5. **Deployment and candidate generation**
- The deployment step loads the most recently saved model version and scores all available Gaia rows
- Prediction outputs are stored in the `predictions` table with full-run replacement
- Non-confirmed rows are ranked by likelihood and written to `new_exoplanet_candidates`
- Candidate confidence levels are computed relative to the learned decision threshold
- Confirmed-host rows are scored directly to append reinforcement examples even when source-id overlap is sparse

## Configuration

All configurable parameters should be defined in `gaiaml/config/config.yaml`. This includes:
- Data source URLs and API endpoints
- Feature lists and engineering parameters
- XGBoost hyperparameters
- Train/test split ratios
- Output paths and logging levels
- Database location and persistence settings

Important currently used config keys:
- `database_settings.database_file_path`
- `logging.log_file_path`

## Testing

Unit tests are located in the `gaiaml/src/tests/` directory and follow the naming convention `test_*.py`. To run tests:

```bash
python -m pytest gaiaml/src/tests/ -v
```

Or use `test` from the main menu of the CLI.

The current regression suite focuses on:
- Data validation and cleaning logic
- Feature engineering transformations
- Model training and prediction workflows
- Reinforcement-loop behavior
- Database persistence and candidate replacement logic

## Model Management

Trained models are saved as versioned JSON files under `gaiaml/src/models/`.

Model versions are also stored in SQLite (`model_versioning`) with metadata:
- Training date
- Model version string
- Performance metrics
- Model artifact path

This makes it straightforward to inspect, compare, and redeploy earlier versions of the trained classifier as the pipeline evolves.
