# This is the main entry file for GaiaML
# From here, the CLI is launched, and the main interaction loop is started.

# Placeholder showing the entry point for the GaiaML application. 
# The actual logic, XGBoost and CLI handling are implemented in the other modules.
try:
    from .cli import start_cli
except ImportError:
    # Allow running this module directly when the package is not installed.
    from cli import start_cli


def main():
    start_cli()


if __name__ == "__main__":
    main()  # Start the command line interface