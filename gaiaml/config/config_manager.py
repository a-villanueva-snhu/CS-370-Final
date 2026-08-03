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

def edit_config(key, value):
    """
    Edits a specific configuration setting in the YAML file.
    Args:
        key (str): The configuration key to edit.
        value: The new value for the configuration key.
    """
    # if the key is the project name, do not allow edits
    if key == "project_name":
        print("Editing the project name is not allowed.")
        return

    # if the key is nested (e.g., "logging.log_level"), we need to handle that
    if '.' in key:
        keys = key.split('.')
        config = load_config()
        d = config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        with open(os.path.join(_PROJECT_ROOT, 'config', 'config.yaml'), 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)

    yaml_helper.edit_yaml(key, value)

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
    db_path = get_config_value('database_settings.database_file_path', os.path.join(_PROJECT_ROOT, 'gaiaml.db'))
    if not isinstance(db_path, str):
        db_path = os.path.join(_PROJECT_ROOT, 'gaiaml.db')

    conn = sqlite3.connect(db_path)
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

def generate_default_yaml() -> bool:
    """
    Generates a default configuration YAML file if it does not exist.
    """
    default_config = {
            "logging": {
                "log_file_path": os.path.join(os.getcwd(), "logs", "gaiaml.log"),
                "log_level": "INFO"
            },
            "welcome_message": "Welcome to GaiaML! Type 'help' for a list of commands.",
            "requirements_path": os.path.join(os.getcwd(), "config", "requirements.txt"),
            "data_sources": {
                "gaia_dr3": {
                    "url": "https://gea.esac.esa.int/archive/",
                    "local_path": os.path.join(os.getcwd(), "data", "gaia_dr3")
                }
            },
            "database_settings": {
                "database_file_path": os.path.join(os.getcwd(), "gaiaml.db")
            }
    }
    try:
        with open(os.path.join(_PROJECT_ROOT, 'config', 'config.yaml'), 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(default_config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Failed to generate default YAML: {e}")
        return False
        