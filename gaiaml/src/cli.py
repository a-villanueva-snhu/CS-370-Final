# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

import sys
import os
import logs.logger as logger


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
                print("  exit/quit/q/e - Exit the CLI")
                # Add more commands as needed

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