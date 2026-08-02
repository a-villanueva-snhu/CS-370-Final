## This is main Database file for the project. 
# It contains all the functions to interact with the database. 
# It is used by the other files in the project to store and 
# retrieve data from the database.

import sqlite3
from logs import logger
import src.utils.crud_helper as crud

def initialize_database():
    """
    Initializes the SQLite database and creates necessary tables if they don't exist.
    This function should be called at the start of the application to ensure the database is ready for use.
    """
    # Setup the database connection and cursor
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    logger.log_info("Database connection established.")

    logger.log_info("Checking and creating tables if they do not exist...")
    logger.log_info("This may take a few moments, please wait...")

    # Create table schemas 
    # Gaia DR3 data table schema
    # check if the table already exists before creating it
    if not crud.table_exists(cursor, 'gaia_dr3_data'):
        crud.create_table(cursor, 'gaia_dr3_data', [
            'source_id INTEGER PRIMARY KEY',
            'ra REAL',
            'dec REAL',
            'parallax REAL',
            'phot_g_mean_mag REAL',
            'phot_bp_mean_mag REAL',
            'phot_rp_mean_mag REAL'
        ])

    # NasaEA data table schema
    # check if the table already exists before creating it
    if not crud.table_exists(cursor, 'nasaea_data'):
        crud.create_table(cursor, 'nasaea_data', [
            'id INTEGER PRIMARY KEY',
            'name TEXT',
            'ra REAL',
            'dec REAL',
            'magnitude REAL'
        ])

    # Gaia test data table schema
    # check if the table already exists before creating it
    if not crud.table_exists(cursor, 'test_data'):
        crud.create_table(cursor, 'test_data', [
            'source_id INTEGER PRIMARY KEY',
            'ra REAL',
            'dec REAL',
            'parallax REAL',
            'phot_g_mean_mag REAL',
            'phot_bp_mean_mag REAL',
            'phot_rp_mean_mag REAL'
        ])

    # Model versioning table schema
    # check if the table already exists before creating it
    if not crud.table_exists(cursor, 'model_versioning'):
        crud.create_table(cursor, 'model_versioning', [
            'version TEXT PRIMARY KEY',
            'date_created TEXT',
            'accuracy REAL',
            'precision REAL',
            'recall REAL'
        ])

    ## Create a test table 
    if not crud.table_exists(cursor, 'test_table'):
        crud.create_table(cursor, 'test_table', ['id INTEGER PRIMARY KEY', 'name TEXT', 'age INTEGER'])

    ## Commit the changes and close the connection
    conn.commit()

    ## Test print the tables in the database
    crud.print_tables(cursor)

    ## Close the connection
    conn.close()

## external functions
# # This function is used to insert data into the database. It takes a table name and a list of tuples as input.
def insert_data(table_name, data):
    """
    Insert data into the database.

    :param table_name: Name of the table to insert data into
    :param data: List of tuples containing the data to insert
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create a placeholder string for the number of columns in the data
    placeholders = ', '.join(['?'] * len(data[0]))

    # Create the SQL query to insert data
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"

    # Execute the query and commit the changes
    cursor.executemany(query, data)
    conn.commit()

    # Close the connection
    conn.close()

def is_database_initialized():
    """
    Check if the database is initialized by verifying the existence of required tables.

    :return: True if the database is initialized, False otherwise
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Check for the existence of required tables
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
def fetch_data(table_name, limit=10):
    """
    Fetch data from the database.

    :param table_name: Name of the table to fetch data from
    :param limit: Number of rows to fetch (default is 10)
    :return: List of tuples containing the fetched data
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to fetch data
    query = f"SELECT * FROM {table_name} LIMIT {limit}"

    # Execute the query and fetch the data
    cursor.execute(query)
    data = cursor.fetchall()

    # Close the connection
    conn.close()

    return data


def get_whole_table(table_name):
    """
    Fetch all data from the specified table.

    :param table_name: Name of the table to fetch data from
    :return: List of tuples containing the fetched data
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to fetch all data
    query = f"SELECT * FROM {table_name}"

    # Execute the query and fetch the data
    cursor.execute(query)
    data = cursor.fetchall()

    # Close the connection
    conn.close()

    return data


def clean_null_and_invalid_data(table_name):
    """
    Clean null and invalid data from the specified table.

    :param table_name: Name of the table to clean data from
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to delete rows with null or invalid values
    query = f"DELETE FROM {table_name} WHERE source_id IS NULL OR ra IS NULL OR dec IS NULL OR parallax IS NULL OR phot_g_mean_mag IS NULL OR phot_bp_mean_mag IS NULL OR phot_rp_mean_mag IS NULL"

    # Execute the query and commit the changes
    cursor.execute(query)
    conn.commit()

    # Close the connection
    conn.close()

def copy_table(source_table, destination_table):
    """
    Copy data from one table to another.

    :param source_table: Name of the source table
    :param destination_table: Name of the destination table
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to copy data from source_table to destination_table
    query = f"INSERT INTO {destination_table} SELECT * FROM {source_table}"

    # Execute the query and commit the changes
    cursor.execute(query)
    conn.commit()

    # Close the connection
    conn.close()

def delete_table(table_name):
    """
    Delete the specified table from the database.

    :param table_name: Name of the table to delete
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to delete the table
    query = f"DROP TABLE IF EXISTS {table_name}"

    # Execute the query and commit the changes
    cursor.execute(query)
    conn.commit()

    # Close the connection
    conn.close()

def update_table(table_name, set_clause, where_clause):
    """
    Update data in the specified table.

    :param table_name: Name of the table to update
    :param set_clause: SET clause for the update query (e.g., "column1 = value1, column2 = value2")
    :param where_clause: WHERE clause for the update query (e.g., "id = 1")
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to update data in the table
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

    # Execute the query and commit the changes
    cursor.execute(query)
    conn.commit()

    # Close the connection
    conn.close()

def delete_data(table_name, where_clause):
    """
    Delete data from the specified table.

    :param table_name: Name of the table to delete data from
    :param where_clause: WHERE clause for the delete query (e.g., "id = 1")
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to delete data from the table
    query = f"DELETE FROM {table_name} WHERE {where_clause}"

    # Execute the query and commit the changes
    cursor.execute(query)
    conn.commit()

    # Close the connection
    conn.close()

def get_table_schema(table_name):
    """
    Get the schema of the specified table.

    :param table_name: Name of the table to get the schema for
    :return: List of tuples containing the column names and types
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to get the table schema
    query = f"PRAGMA table_info({table_name})"

    # Execute the query and fetch the schema
    cursor.execute(query)
    schema = cursor.fetchall()

    # Close the connection
    conn.close()

    return schema

def get_table_names():
    """
    Get the names of all tables in the database.

    :return: List of table names
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Create the SQL query to get the table names
    query = "SELECT name FROM sqlite_master WHERE type='table'"

    # Execute the query and fetch the table names
    cursor.execute(query)
    table_names = [row[0] for row in cursor.fetchall()]

    # Close the connection
    conn.close()

    return table_names

def clean_data_and_clone():
    """
    Clean the data in the 'gaia_dr3_data' table and clone it to a new table.
    This function removes rows with null or invalid values and creates a new table
    with the cleaned data.
    """
    # Clean the data in the 'gaia_dr3_data' table
    clean_null_and_invalid_data('gaia_dr3_data')

    # Create a new table name for the cleaned data
    cleaned_table_name = 'gaia_dr3_data_cleaned'

    # Delete the cleaned table if it already exists
    delete_table(cleaned_table_name)

    # Clone the cleaned data to the new table
    copy_table('gaia_dr3_data', cleaned_table_name)

def normalize_table(table_name='gaia_dr3_data_cleaned'):
    """
    Normalize the data in the specified table.
    This function normalizes the numerical columns in the table to a range of [0, 1].
    """
    conn = sqlite3.connect('gaiaml.db')
    cursor = conn.cursor()

    # Get the schema of the cleaned table
    schema = get_table_schema(table_name)

    # Identify numerical columns for normalization
    numerical_columns = [col[1] for col in schema if col[2] in ('REAL', 'INTEGER') and col[1] != 'source_id']

    # Normalize each numerical column
    for column in numerical_columns:
        # Get the min and max values for the column
        cursor.execute(f"SELECT MIN({column}), MAX({column}) FROM {table_name}")
        min_val, max_val = cursor.fetchone()

        # Normalize the column if min and max are not equal
        if min_val != max_val:
            cursor.execute(f"""
                UPDATE {table_name}
                SET {column} = ({column} - {min_val}) / ({max_val} - {min_val})
            """)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def trim_gaia_data(data):
    """
    Trim the Gaia DR3 data to include only relevant columns for model training.
    This function selects specific columns from the input data and returns a new DataFrame.

    :param data: Input DataFrame containing Gaia DR3 data
    :return: Trimmed DataFrame with selected columns
    """
    # Define the relevant columns to keep
    relevant_columns = ['source_id', 'ra', 'dec', 'parallax', 'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag']

    # Select only the relevant columns from the input data
    trimmed_data = data[relevant_columns]

    return trimmed_data