## This is main Database file for the project.
# It contains all the functions to interact with the database.
# It is used by the other files in the project to store and
# retrieve data from the database.

import os
import sqlite3
from typing import Literal, overload
import pandas as pd
import numpy as np
import logs.logger as logger
import src.utils.crud_helper as crud
from config import config_manager

## Database Schemas
schemas = {
    'gaia_dr3_data': [
        'is_confirmed_host INTEGER',
        'source_id INTEGER PRIMARY KEY',
        'ra REAL',
        'dec REAL',
        'parallax REAL',
        'phot_g_mean_mag REAL',
        'phot_bp_mean_mag REAL',
        'phot_rp_mean_mag REAL'
    ],
    'nasaea_data': [
        'id INTEGER PRIMARY KEY',
        'name TEXT',
        'ra REAL',
        'dec REAL',
        'magnitude REAL'
    ],
    'confirmed_exoplanets_data': [
        'id INTEGER PRIMARY KEY',
        'name TEXT',
        'ra REAL',
        'dec REAL',
        'magnitude REAL',
        'is_confirmed_host INTEGER',
    ],
    'preprocessed_training_data': [
        'source_id INTEGER PRIMARY KEY',
        'ra REAL',
        'dec REAL',
        'parallax REAL',
        'phot_g_mean_mag REAL',
        'phot_bp_mean_mag REAL',
        'phot_rp_mean_mag REAL',
        'is_confirmed_host INTEGER'
    ],
    'test_data': [
        'source_id INTEGER PRIMARY KEY',
        'ra REAL',
        'dec REAL',
        'parallax REAL',
        'phot_g_mean_mag REAL',
        'phot_bp_mean_mag REAL',
        'phot_rp_mean_mag REAL',
        'is_confirmed_host INTEGER',
    ],
    'model_versioning': [
        'version TEXT PRIMARY KEY',
        'date_created TEXT',
        'f1 REAL',
        'accuracy REAL',
        'precision REAL',
        'recall REAL',
        'model_json TEXT'
    ],
    'predictions': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'source_id INTEGER',
        'prediction REAL'
    ],
    'new_exoplanet_candidates': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'source_id INTEGER',
        'likelihood REAL'
    ],
    'reinforcement_examples': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'source_id INTEGER',
        'is_confirmed_host INTEGER',
        'prediction REAL',
        'reinforced_at TEXT'
    ],
}


def _get_database_path() -> str:
    """Return a concrete SQLite path that satisfies strict typing."""
    default_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')),
        'gaiaml.db'
    )
    db_path = config_manager.get_config_value('database_settings.database_file_path', default_path)
    if not isinstance(db_path, str):
        return default_path
    return db_path


def initialize_database():
    """
    Initializes the SQLite database and creates necessary tables if they don't exist.
    This function should be called at the start of the application to ensure the database is ready for use.
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    logger.log_info("Database connection established.")
    logger.log_info("Checking and creating tables if they do not exist...")
    logger.log_info("This may take a few moments, please wait...")

    if not crud.table_exists(cursor, 'gaia_dr3_data'):
        crud.create_table(cursor, 'gaia_dr3_data', schemas['gaia_dr3_data'])

    if not crud.table_exists(cursor, 'nasaea_data'):
        crud.create_table(cursor, 'nasaea_data', schemas['nasaea_data'])

    if not crud.table_exists(cursor, 'confirmed_exoplanets_data'):
        crud.create_table(cursor, 'confirmed_exoplanets_data', schemas['confirmed_exoplanets_data'])

    if not crud.table_exists(cursor, 'test_data'):
        crud.create_table(cursor, 'test_data', schemas['test_data'])

    if not crud.table_exists(cursor, 'model_versioning'):
        crud.create_table(cursor, 'model_versioning', schemas['model_versioning'])
    if not crud.table_exists(cursor, 'predictions'):
        crud.create_table(cursor, 'predictions', schemas['predictions'])
    if not crud.table_exists(cursor, 'new_exoplanet_candidates'):
        crud.create_table(cursor, 'new_exoplanet_candidates', schemas['new_exoplanet_candidates'])
    if not crud.table_exists(cursor, 'reinforcement_examples'):
        crud.create_table(cursor, 'reinforcement_examples', schemas['reinforcement_examples'])

    else:
        cursor.execute("PRAGMA table_info(model_versioning)")
        model_versioning_columns = {row[1] for row in cursor.fetchall()}
        if 'model_json' not in model_versioning_columns:
            cursor.execute("ALTER TABLE model_versioning ADD COLUMN model_json TEXT")
        if 'f1' not in model_versioning_columns:
            cursor.execute("ALTER TABLE model_versioning ADD COLUMN f1 REAL")

    if not crud.table_exists(cursor, 'test_table'):
        crud.create_table(cursor, 'test_table', ['id INTEGER PRIMARY KEY', 'name TEXT', 'age INTEGER'])

    conn.commit()
    crud.print_tables(cursor)
    conn.close()


def regenerate_table(table_name, schema=None):
    """
    Regenerates a table in the database by dropping it if it exists and creating it with the specified schema.

    :param table_name: Name of the table to regenerate
    :param schema: List of column definitions for the new table
    """
    if schema is None and table_name in schemas:
        schema = schemas[table_name]
    elif schema is None:
        raise ValueError(f"No schema provided for table '{table_name}' and no predefined schema found.")

    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    crud.drop_table(cursor, table_name)
    crud.create_table(cursor, table_name, schema)

    conn.commit()
    conn.close()


## external functions
# # This function is used to insert data into the database. It takes a table name and a list of tuples as input.
def insert_data(table_name, data):
    """
    Insert data into the database.

    :param table_name: Name of the table to insert data into
    :param data: List of tuples containing the data to insert
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(data[0]))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"

    cursor.executemany(query, data)
    conn.commit()
    conn.close()


def is_database_initialized():
    """
    Check if the database is initialized by verifying the existence of required tables.

    :return: True if the database is initialized, False otherwise
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    required_tables = ['gaia_dr3_data', 'nasaea_data', 'model_versioning']
    for table in required_tables:
        if not crud.table_exists(cursor, table):
            conn.close()
            return False

    conn.close()
    return True


## This function is used to fetch data from the database. It takes a table name and an optional limit as input.
# parameters:
# - table_name: Name of the table to fetch data from
# - limit: Number of rows to fetch (default is 10)
@overload
def fetch_data(table_name: str, limit: int = 10, *, as_dataframe: Literal[False] = False) -> list[tuple]:
    ...
@overload
def fetch_data(table_name: str, limit: int = 10, *, as_dataframe: Literal[True]) -> "pd.DataFrame":
    ...
def fetch_data(table_name, limit=10, as_dataframe=False):
    """
    Fetch data from the database.

    :param table_name: Name of the table to fetch data from
    :param limit: Number of rows to fetch (default is 10)
    :param as_dataframe: When True, return a pandas DataFrame
    :return: List of tuples containing the fetched data or a pandas DataFrame
    """
    conn = sqlite3.connect(_get_database_path())

    query = f"SELECT * FROM {table_name}" if limit == -1 else f"SELECT * FROM {table_name} LIMIT {limit}"

    if as_dataframe:
        data = pd.read_sql_query(query, conn)
    else:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

    conn.close()
    return data


def get_whole_table(table_name):
    """
    Fetch all data from the specified table.

    :param table_name: Name of the table to fetch data from
    :return: List of tuples containing the fetched data
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    data = cursor.fetchall()

    conn.close()
    return data


def clean_null_and_invalid_data(table_name):
    """
    Clean null and invalid data from the specified table.

    :param table_name: Name of the table to clean data from
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = (
        f"DELETE FROM {table_name} WHERE source_id IS NULL OR ra IS NULL OR dec IS NULL "
        "OR parallax IS NULL OR phot_g_mean_mag IS NULL OR phot_bp_mean_mag IS NULL "
        "OR phot_rp_mean_mag IS NULL"
    )

    cursor.execute(query)
    conn.commit()
    conn.close()


def copy_table(source_table, destination_table):
    """
    Copy data from one table to another.

    :param source_table: Name of the source table
    :param destination_table: Name of the destination table
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"INSERT INTO {destination_table} SELECT * FROM {source_table}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def delete_table(table_name):
    """
    Delete the specified table from the database.

    :param table_name: Name of the table to delete
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"DROP TABLE IF EXISTS {table_name}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def update_table(table_name, set_clause, where_clause):
    """
    Update data in the specified table.

    :param table_name: Name of the table to update
    :param set_clause: SET clause for the update query (e.g., "column1 = value1, column2 = value2")
    :param where_clause: WHERE clause for the update query (e.g., "id = 1")
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def delete_data(table_name, where_clause):
    """
    Delete data from the specified table.

    :param table_name: Name of the table to delete data from
    :param where_clause: WHERE clause for the delete query (e.g., "id = 1")
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"DELETE FROM {table_name} WHERE {where_clause}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def get_table_schema(table_name):
    """
    Get the schema of the specified table.

    :param table_name: Name of the table to get the schema for
    :return: List of tuples containing the column names and types
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = f"PRAGMA table_info({table_name})"
    cursor.execute(query)
    schema = cursor.fetchall()

    conn.close()
    return schema


def get_table_names():
    """
    Get the names of all tables in the database.

    :return: List of table names
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    query = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(query)
    table_names = [row[0] for row in cursor.fetchall()]

    conn.close()
    return table_names


def clean_data_and_clone():
    """
    Clean the data in the 'gaia_dr3_data' table and clone it to a new table.
    This function removes rows with null or invalid values and creates a new table
    with the cleaned data.
    """
    clean_null_and_invalid_data('gaia_dr3_data')

    cleaned_table_name = 'gaia_dr3_data_cleaned'
    delete_table(cleaned_table_name)
    copy_table('gaia_dr3_data', cleaned_table_name)


def normalize_table(table_name='gaia_dr3_data_cleaned'):
    """
    Normalize the data in the specified table.
    This function normalizes the numerical columns in the table to a range of [0, 1].
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    schema = get_table_schema(table_name)
    numerical_columns = [col[1] for col in schema if col[2] in ('REAL', 'INTEGER') and col[1] != 'source_id']

    for column in numerical_columns:
        cursor.execute(f"SELECT MIN({column}), MAX({column}) FROM {table_name}")
        min_val, max_val = cursor.fetchone()

        if min_val != max_val:
            cursor.execute(
                f"""
                UPDATE {table_name}
                SET {column} = ({column} - {min_val}) / ({max_val} - {min_val})
                """
            )

    conn.commit()
    conn.close()


def trim_gaia_data(data):
    """
    Trim the Gaia DR3 data to include only relevant columns for model training.
    This function selects specific columns from the input data and returns a new DataFrame.

    :param data: Input DataFrame containing Gaia DR3 data
    :return: Trimmed DataFrame with selected columns
    """
    relevant_columns = ['source_id', 'ra', 'dec', 'parallax', 'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag']
    trimmed_data = data[relevant_columns]
    return trimmed_data


def save_model_version_json(version, date_created, f1, accuracy, precision, recall, model_json):
    """
    Save the model version information to the 'model_versioning' table in the database.

    :param version: Version identifier for the model
    :param date_created: Date when the model was created
    :param f1: F1 score of the model
    :param accuracy: Accuracy of the model
    :param precision: Precision of the model
    :param recall: Recall of the model
    :param model_json: JSON string representation of the model
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(model_versioning)")
    available_columns = {row[1] for row in cursor.fetchall()}

    fields = ['version', 'date_created', 'f1', 'accuracy', 'precision', 'recall']
    values = [version, date_created, f1, accuracy, precision, recall]

    if 'model_json' in available_columns:
        fields.append('model_json')
        values.append(model_json)
    else:
        logger.log_warning(
            "model_versioning is missing the 'model_json' column. Saving version metadata without the model path."
        )

    placeholders = ', '.join(['?'] * len(fields))
    query = f"INSERT INTO model_versioning ({', '.join(fields)}) VALUES ({placeholders})"

    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()


def load_model_from_versioning(version):
    """
    Load a model from the 'model_versioning' table in the database based on the specified version.

    :param version: Version identifier for the model to load
    :return: JSON string representation of the model or None if not found
    """
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(model_versioning)")
    available_columns = {row[1] for row in cursor.fetchall()}

    if 'model_json' not in available_columns:
        logger.log_error("model_versioning is missing the 'model_json' column. Cannot load model.")
        conn.close()
        return None

    query = "SELECT model_json FROM model_versioning WHERE version = ?"
    cursor.execute(query, (version,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    logger.log_warning(f"No model found for version {version}.")
    return None


def get_latest_model_version():
    """Return the most recent model version or None if no versions exist."""
    conn = sqlite3.connect(_get_database_path())
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM model_versioning ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def store_predictions(table_name, predictions):
    """
    Store model predictions in the specified table in the database.

    :param table_name: Name of the table to store predictions
    :param predictions: List or array of predictions to store
    """
    conn = sqlite3.connect(_get_database_path())

    if table_name == "predictions":
        if isinstance(predictions, pd.DataFrame):
            if not {"source_id", "prediction"}.issubset(predictions.columns):
                raise ValueError("predictions DataFrame must include 'source_id' and 'prediction' columns")
            payload = predictions[["source_id", "prediction"]]
            payload.to_sql("predictions", conn, if_exists="append", index=False)
        else:
            values = np.asarray(predictions).reshape(-1)
            pd.DataFrame({"prediction": values}).to_sql("predictions", conn, if_exists="append", index=False)

    elif table_name == "new_exoplanet_candidates":
        if isinstance(predictions, pd.DataFrame):
            if not {"source_id", "likelihood"}.issubset(predictions.columns):
                raise ValueError("new_exoplanet_candidates DataFrame must include 'source_id' and 'likelihood' columns")
            payload = predictions[["source_id", "likelihood"]]
            payload.to_sql("new_exoplanet_candidates", conn, if_exists="append", index=False)
        else:
            raise ValueError("new_exoplanet_candidates storage requires a DataFrame with source_id and likelihood")

    else:
        raise ValueError(f"Unsupported predictions table: {table_name}")

    conn.commit()
    conn.close()


def append_reinforcement_examples(reinforcement_df):
    """Append verified examples to the reinforcement_examples table for future training cycles."""
    if reinforcement_df is None or reinforcement_df.empty:
        return

    if not {"source_id", "is_confirmed_host", "prediction"}.issubset(reinforcement_df.columns):
        raise ValueError("reinforcement_df must include source_id, is_confirmed_host, and prediction columns")

    conn = sqlite3.connect(_get_database_path())
    payload = reinforcement_df[["source_id", "is_confirmed_host", "prediction"]].copy()
    payload["reinforced_at"] = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    payload.to_sql("reinforcement_examples", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()