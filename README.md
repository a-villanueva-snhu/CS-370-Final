# CS-499 Capstone Project
Final Project for SNHU CS-499
Aiden Villanueva
July 20, 2026

Version:

1.0.0     |     Added basic description and module breakdown


# Project GaiaML
Project GaiaML is an open-source scientific data tool designed to use eXtreme Gradient Boosted (XGBoost) trees in order to classify Gaia DR3 data against NASA's Exoplanet Archive of known and suspected exoplanet host stars. 

The goal is to show that XGBoost is a strong choice for analyzing large, tabularized data sets such as many astronomical data, and that it is capable of being tuned and trained to accurately classify known systems as well as to create predictions for possible new candidates. 

# Project Structure

The project is organized around data preparation, model training, evaluation, and prediction. Key folders and files are arranged to separate data ingestion, feature engineering, training pipelines, and results.

- config/: YAML file(s) for globalizing variables and model configuration parameters.
- data/: raw data files, cleaned datasets, and lookup tables.
- src/: core project code including data processing, feature engineering, and model utilities.
- docs/: supplementary documentation, notes, and reference material.

# Main Files

- `main.py`: entry point for running the training and prediction workflow.
- `gaia_ & nasa_downloader.py`: handles loading Gaia DR3 data and NASA Exoplanet Archive data, including parsing and validation.
- `preprocessor.py`: creates derived features, handles missing values, and prepares data for XGBoost.
- `xgboost_trainer.py`: trains the XGBoost classifier and saves the trained model.
- `model_evaluator.py`: evaluates model performance on test data and generates metrics.
- `model.py`: runs the trained model on new Gaia DR3 data for candidate classification.

Deprecated artifacts such as `TreasureHuntGame`, `TreasureMaze.py`, and `GameExperience.py` are intentionally excluded from the final project structure and documentation.



