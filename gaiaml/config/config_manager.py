## A general configuration manager for the GaiaML project. 
# This module handles the loading and management of configuration settings from a 
# YAML file.


from config import yaml_helper
import os
import sqlite3


_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

def check_yaml():
    """
    Checks if the YAML configuration file exists and is valid.
    Returns:
        bool: True if the YAML file exists and is valid, False otherwise.
    """
    return yaml_helper.check_yaml()

def open_yaml():
    """ Opens the config.yaml file in the default text editor. """
    yaml_helper.open_yaml_dir()

## Helpers (updated to use yaml_helper)
def load_config():
    """
    Loads configuration settings from a YAML file.
    Args:
        file_path (str): The path to the YAML configuration file.
    Returns:
        dict: A dictionary containing the configuration settings.
    """
    return yaml_helper.load_yaml()

def get_config_value(key, default=None):
    """
    Retrieves a configuration value from the loaded configuration dictionary.
    If the key does not exist, it returns the specified default value.
    """
    config = load_config()
    value = config

    if key in config:
        value = config[key]
    else:
        for part in key.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                value = default
                break

    if isinstance(value, dict) and isinstance(default, str) and default in value:
        value = value[default]

    path_key = key.split('.')[-1]
    if isinstance(default, str) and default.endswith('_path'):
        path_key = default

    if isinstance(value, str) and path_key.endswith('_path'):
        if value.startswith(("/", "\\")):
            value = os.path.join(_PROJECT_ROOT, value.lstrip("/\\"))
        value = os.path.normpath(value)

        if key in ('database_settings.database_file_path', 'database_settings'):
            os.makedirs(os.path.dirname(value), exist_ok=True)

    return value

def check_version_database(key, version):
    """
    Checks the version of the database against the expected version in the configuration.
    This function is a placeholder and should be implemented to perform actual version checking.
    """
    pass

def get_current_date():
    """
    Returns the current date in YYYY-MM-DD format.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def get_next_model_version():
    """
    Returns the next patch version for the model_versioning table.
    """
    conn = sqlite3.connect(get_config_value('database_settings.database_file_path', os.path.join(_PROJECT_ROOT, 'gaiaml.db')))
    cursor = conn.cursor()

    cursor.execute("SELECT version FROM model_versioning ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row is None or not row[0]:
        return "0.0.1"

    version_parts = row[0].split('.')
    if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
        return "0.0.1"

    major, minor, patch = map(int, version_parts)
    return f"{major}.{minor}.{patch + 1}"

def generate_default_yaml():
    """
    Generates a default configuration YAML file if it does not exist.
    """
    yaml_helper.generate_default_yaml()