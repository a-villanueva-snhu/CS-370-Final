# This is the main entry file for GaiaML
# From here, the CLI is launched, and the main interaction loop is started.

# The actual logic, XGBoost and CLI handling are implemented in the other modules.

# from cli import cli
from data.database.sqlite import db as db
import logs.logger as logger
from config import config_manager


def main():
    # Initialize the database
    logger.log_info("Starting GaiaML...")
    logger.log_info("Initializing database...")
    logger.log_info("This may take a few seconds, please wait...")

    try:
        db.initialize_database()  # Initialize the database
        logger.log_info("Database initialized successfully.")
    except Exception as e:
        logger.log_error(f"Error initializing the database: {e}")
        print("Error initializing the database. Please check the logs for more details.")
        return

    ## CHECK for config file existence and validity
    if not config_manager.check_yaml():
        logger.log_warning("Configuration file is missing or invalid. Generating default configuration...")
        try:
            config_manager.generate_default_yaml()
            logger.log_info("Default configuration generated. Please review the config.yaml file.")
            print("Default configuration generated. Please review the config.yaml file.")
        except Exception as e:
            logger.log_error(f"Error generating default configuration: {e}")
            print("Error generating default configuration. Please check the logs for more details.")

    ## Start the CLI
    logger.log_info("Starting GaiaML CLI...")

    # lazy import of cli to avoid circular import issues
    from cli import cli

    try:
        cli.start_cli()  # Start the command line interface
    except Exception as e:
        logger.log_error(f"Error in CLI: {e}")
        print("Error in CLI. Please check the logs for more details.")

if __name__ == "__main__":
    main()  # Start the command line interface