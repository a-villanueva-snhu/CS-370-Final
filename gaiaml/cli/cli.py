# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

import os
from logs import logger
from src.tests.e2e_tester import TestLogger
from config import config_manager

## Starts the CLI to await user commands. This function will run in a loop until 
# the user decides to exit.
#
# Updated to use config_manager for configuration management and logging.
def start_cli():
    print(config_manager.get_config_value("welcome_message", "Error: Welcome message not found in config."))
    print("Type 'help' for a list of commands.")
    while True:
    ## Handle user input commands

        command = input("GaiaML> ")
        match command:
            ## General Commands
            case "exit" | "quit" | "q" | "e":
                print("Exiting GaiaML CLI. Goodbye!")
                break
            case "help":
                print("Available commands:")
                print("  help - Show this help message")
                print("  test - Run tests for the project")
                print("  config - Load configuration for the project")
                print("  logs - Open the log folder")
                print("  download - Download data from Gaia DR3 or NasaEA")
                print("  preprocess - Preprocess the downloaded data")
                print("  train - Train the model with the preprocessed data")
                print("  evaluate - Evaluate the trained model")
                print("  deploy - Deploy the trained model")
                print("  visualize - Visualize the data and model results")


                print("  exit/quit/q/e - Exit the CLI")
                # Add more commands as needed

            ## Testing, config and logging commands
            case "test":
                i = input("Enter the test to run | logger | cli | all | : ")
                match i:
                    case "logger":
                        print("Running logger tests...")
                        ## Uses the e2e_tester.py file to run the logger tests. 
                        # This is a basic test to ensure that the logger is working 
                        # correctly as well as the testing framework. 
                        # It is not a comprehensive test of the logger, 
                        # but it is a good starting point.
                        logger_tester = TestLogger()
                        logger_tester.test_log_info()
                        logger_tester.test_log_warning()
                        logger_tester.test_log_error()
                        logger_tester.test_log_exception()
                        # logger_tester.__exit__(None, None, None)      ## Broken?

                        print("Logger tests complete.")

                    case "cli":
                        print("Running CLI tests...")

                        # TODO: Add actual CLI tests here. For now, we will just print a message.
                        print("The CLI is probably working, if you made it here.")

                        print("CLI tests complete.")

                    case "all":
                        print("Running all tests...")
                        # Call the function to run all automated tests here
                        # e.g., run_all_tests()
                        print("All tests complete.")

                    case "menu":
                        print("Returning to main menu...")
                        break

                    case _:
                        print(f"Unknown test: {i}. Please enter 'logger', 'cli', or 'all'.")

            case "config":
                i = input("Enter the config command | load | open | : ")
                match i:
                    case "load":
                        print("Loading configuration...")
                        config = config_manager.load_config()
                        print("Configuration loaded.")
                    case "open":
                        print("Opening configuration file...")
                        config_manager.open_yaml()
                    case "menu":
                        print("Returning to main menu...")
                        break
                    case _:
                        print(f"Unknown config command: {i}. Please enter 'load' or 'open'.")

            ## Opens the log folder in the file explorer. This is useful for quickly accessing log files.
            case "logs":
                print("Opening log folder...")
                log_folder = os.path.join(os.getcwd(), "logs")
                if not os.path.exists(log_folder):
                    os.makedirs(log_folder)
                os.startfile(log_folder)

            ## Data Downloading Commands
            case "download":
                command = input("Enter the data source to download (g= Gaia DR3; n = NasaEA): ")

                match command:
                    case "g":
                        print("Downloading Gaia DR3 data...")
                        # Call the function to download Gaia DR3 data here
                        # e.g., download_gaia_dr3_data()
                        print("Download complete.")
                    case "n":
                        print("Downloading NasaEA data...")
                        # Call the function to download NasaEA data here
                        # e.g., download_nasaea_data()
                        print("Download complete.")
                    case "test":
                        print("Downloading test data with confirmed exoplanets...")
                        ## Call the function to download test data here
                        # e.g., download_test_data()
                    case "menu":
                        print("Returning to main menu...")
                        break
                    case _:
                        print(f"Unknown data source: {command}. Please enter 'g' for Gaia DR3 or 'n' for NasaEA.")

            ## Data Preprocessing Commands
            case "preprocess":
                print("Preprocessing data...")
                # Call the function to preprocess data here
                # e.g., preprocess_data()
                print("Preprocessing complete.")

            ## Model Training Commands
            case "train":
                print("Training model...")
                # Call the function to train the model here
                # e.g., train_model()
                print("Model training complete.")

            ## Model Evaluation Commands
            case "evaluate":
                print("Evaluating model...")
                # Call the function to evaluate the model here
                # e.g., evaluate_model()
                print("Model evaluation complete.")

            ## Model Deployment Commands
            case "deploy":
                print("Deploying model...")
                # Call the function to deploy the model here
                # e.g., deploy_model()
                print("Model deployment complete.")

            ## Visualization Commands
            case "visualize":
                print("Visualizing data...")
                # Call the function to visualize data here
                # e.g., visualize_data()
                print("Visualization complete.")

            case _:
                print(f"Unknown command: {command}. Type 'help' for a list of commands.")