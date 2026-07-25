## A simple yaml loader utility for the GaiaML project.

import os

import yaml
import os

file_path = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_yaml():
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def open_yaml_dir():
    """ Opens the directory containing the YAML files in the file explorer. """
    yaml_dir = os.path.dirname(os.path.abspath(file_path))
    os.startfile(yaml_dir)

def check_yaml():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError as e:
        print(f"Error in YAML file {file_path}: {e}")
        return False

def get_requirements():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def get_config_value(key, default=None):
    config = load_yaml()
    return config.get(key, default)