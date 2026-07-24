# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

import os
from logs import logger

## Starts the CLI to await user commands. This function will run in a loop until 
# the user decides to exit.
def start_cli():
    print("Welcome to GaiaML CLI!")
    print("Type 'help' for a list of commands.")
    while True:
    ## Handle user input and commands

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
                        ## Call the function to run logger tests here
                        logger.log_info("This is an info message for testing.")
                        logger.log_warning("This is a warning message for testing.")
                        logger.log_error("This is an error message for testing.")

                        logger.log_exception("This is an exception message for testing.")
                        print("Logger tests complete.")

                    case "cli":
                        print("Running CLI tests...")
                        # Call the function to run CLI tests here
                        # e.g., run_cli_tests()
                        print("CLI tests complete.")

                    case "all":
                        print("Running all tests...")
                        # Call the function to run all tests here
                        # e.g., run_all_tests()
                        print("All tests complete.")
                    case _:
                        print(f"Unknown test: {i}. Please enter 'logger', 'cli', or 'all'.")

            case "config":
                print("Loading configuration...")
                # Call the function to load configuration here
                # e.g., load_configuration()
                print("Configuration loaded.")

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