# This is the main entry file for GaiaML
# From here, the CLI is launched, and the main interaction loop is started.

# Placeholder showing the entry point for the GaiaML application. 
# The actual logic, XGBoost and CLI handling are implemented in the other modules.

from cli import cli


def main():
    cli.start_cli()


if __name__ == "__main__":
    main()  # Start the command line interface