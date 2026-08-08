# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

import os
import shlex
import pandas as pd
import xgboost as xgb
import logs.logger as logger
from src.tests.e2e_tester import TestLogger
from config import config_manager
from src.preprocessing import preprocessor
# from src.utils import gaia_downloader  ## Moved to lazy load in command handling to avoid load time issues with sqlite and astroquery. These modules are not needed for the CLI to start, and can be loaded when needed.

def _parse_positive_int(value, default_value):
    try:
        parsed = int(value)
        if parsed > 0:
            return parsed
    except (TypeError, ValueError):
        pass
    return default_value


def _execute_command(command_line):
    if not command_line.strip():
        return True

    try:
        parts = shlex.split(command_line)
    except ValueError as e:
        print(f"Invalid command syntax: {e}")
        return True

    if not parts:
        return True

    command = parts[0].lower()
    args = parts[1:]

    match command:
            ## General Commands
            case "exit" | "quit" | "q" | "e":
                print("Exiting GaiaML CLI. Goodbye!")
                return False
            case "help":
                print("Available commands:")
                print("  help - Show this help message")
                print("  test - Run tests for the project")
                print("  config - Load configuration for the project")
                print("  logs - Open the log folder")
                print("  download [g|c|n] [count] - Download Gaia DR3, confirmed exoplanets, or NasaEA data")
                print("  preprocess - Preprocess the downloaded data")
                print("  train - Train the model with the preprocessed data")
                print("  evaluate - Evaluate the trained model")
                print("  deploy - Deploy the trained model")
                print("  automate-reinforce [max_iters] [target_accuracy] [target_precision] - Train repeatedly until metrics meet the target")
                print("  candidates [limit] - Show the highest-likelihood non-confirmed candidate predictions")
                print("  settings regen <table_name> - Regenerate a database table")
                print("  Chained commands: use ';' between commands")
                print("    Example: download g 200; download c 50; preprocess; train; deploy")
                print("  visualize - Visualize the data and model results")


                print("  exit/quit/q/e - Exit the CLI")
                # Add more commands as needed

            ## Testing, config and logging commands
            case "test":
                i = args[0].lower() if args else input("Enter the test to run | logger | cli | all | : ").strip().lower()
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
                        return True

                    case _:
                        print(f"Unknown test: {i}. Please enter 'logger', 'cli', or 'all'.")

            case "config":
                i = args[0].lower() if args else input("Enter the config command | load | open | edit | : ").strip().lower()
                match i:
                    case "load":
                        print("Loading configuration...")
                        config = config_manager.load_config()
                        print("Configuration loaded.")
                    case "open":
                        print("Opening configuration file...")
                        config_manager.open_yaml()
                    case "edit":
                        # Allow edits until the user decides to return to the main menu
                        while True:
                            # print config keys and values
                            config = config_manager.load_config()

                            for key, value in config.items():
                                print(f"{key}: {value}")

                            c = input("Enter the config key to edit (e.g., 'database_settings.database_file_path'): ")
                            v = input(f"Enter the new value for '{c}': ")
                            config_manager.edit_config(c, v)

                            # sanity check
                            config = config_manager.load_config()
                            print("Updated configuration:")
                            for key, value in config.items():
                                print(f"{key}: {value}")

                            print("'Back' to return to the main menu, or 'edit' to edit another config value.")
                            choice = input("Enter your choice: ").strip().lower()
                            if choice == "back":
                                break
                            elif choice == "edit":
                                continue
                            else:
                                print("Unknown choice. Returning to main menu...")
                                break

                    case "menu":
                        print("Returning to main menu...")
                        return True
                    case _:
                        print(f"Unknown config command: {i}. Please enter 'load', 'open', 'edit', or 'menu'.")

            ## Opens the log folder in the file explorer. This is useful for quickly accessing log files.
            case "logs":
                print("Opening log folder...")
                log_folder = os.path.join(os.getcwd(), "logs")
                if not os.path.exists(log_folder):
                    os.makedirs(log_folder)
                os.startfile(log_folder)

            ## Data Downloading Commands
            case "download":
                logger.log_info("Initializing GaiaDownloader, please wait...")
                import src.utils.gaia_downloader as gaia_downloader

                source = args[0].lower() if args else input("Enter the data source to download (g= Gaia DR3 | c = Confirmed Exoplanets | n = NasaEA): ").strip().lower()
                count = _parse_positive_int(args[1], 100) if len(args) > 1 else None

                match source:
                    case "g" | "gaia" | "gaia_dr3":
                        logger.log_info("Downloading Gaia DR3 data...")
                        gaia_count = count if count is not None else _parse_positive_int(input("Row count for Gaia DR3 download (default 100): ").strip() or "100", 100)
                        gaia_downloader.download_gaia_dr3_data(count=gaia_count)
                        logger.log_info("Download complete.")
                    case "n" | "nasa" | "nasaea":
                        logger.log_info("Downloading NasaEA data...")
                        # Call the function to download NasaEA data here
                        # e.g., download_nasaea_data()
                        logger.log_info("Download complete.")
                    case "c" | "confirmed" | "confirmed_exoplanets":
                        logger.log_info("Downloading confirmed exoplanets data...")
                        confirmed_count = count if count is not None else _parse_positive_int(input("Row count for confirmed exoplanets download (default 10): ").strip() or "10", 10)
                        gaia_downloader.download_confirmed_exoplanets_data(count=confirmed_count)
                        logger.log_info("Confirmed exoplanets data download complete.")
                    case "menu":
                        print("Returning to main menu...")
                        return True
                    case _:
                        print(f"Unknown data source: {source}. Please enter 'g' for Gaia DR3, 'c' for Confirmed Exoplanets, or 'n' for NasaEA.")

            ## Data Preprocessing Commands
            case "preprocess":
                logger.log_info("Starting data preprocessing...")
                from data.database.sqlite import db
                import src.preprocessing.preprocessor as preprocessor
                # import pandas as pd

                print("Preprocessing Gaia data...")
                df = db.fetch_data("gaia_dr3_data", -1, as_dataframe=True)
                if df.empty:
                    logger.log_warning("gaia_dr3_data is empty. Falling back to test_data for preprocessing.")
                    df = db.fetch_data("test_data", -1, as_dataframe=True)
                preprocessor.preprocess_gaia_data(df)


                print("Preprocessing confirmed exoplanets data...")
                df_confirmed = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)
                preprocessor.preprocess_confirmed_exoplanets_data(df_confirmed, target_column='is_confirmed_host')

                print("Creating training dataset from Gaia DR3...")
                from src.preprocessing.preprocessor import create_training_dataset_from_gaia_dr3
                X_combined, y_combined = create_training_dataset_from_gaia_dr3()

                print("Preprocessing complete.")

            ## Model Training Commands
            case "train":
                logger.log_info("Starting model training...")
                from src.training import xgboost_trainer
                from data.database.sqlite import db
                from src.preprocessing import preprocessor

                logger.log_info("preprocessing data for training...")
                X, y = preprocessor.create_training_dataset_from_gaia_dr3()

                xgboost_trainer.train_xgboost_model(X, y)

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
                import src.models.run_model as run_model
                print("Running model on new data...")
                run_model.run_model()
                print("Model deployment complete.")

            case "automate-reinforce" | "automate_reinforce":
                import src.models.run_model as run_model
                from src.preprocessing import preprocessor
                from src.training import xgboost_trainer
                from data.database.sqlite import db

                max_iterations = int(args[0]) if len(args) > 0 and args[0].isdigit() else 5
                target_accuracy = float(args[1]) if len(args) > 1 else 0.99
                target_precision = float(args[2]) if len(args) > 2 else 0.99

                print(f"Starting reinforcement training loop for up to {max_iterations} iterations...")

                def train_iteration(iteration):
                    X, y = preprocessor.create_training_dataset_from_gaia_dr3()
                    model, _, _ = xgboost_trainer.train_xgboost_model(X, y)
                    return {"model": model, "iteration": iteration, "X": X, "y": y}

                def evaluate_iteration(train_result, iteration):
                    metrics = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}
                    try:
                        from sklearn.metrics import accuracy_score, precision_score, recall_score
                        confirmed_df = db.fetch_data("confirmed_exoplanets_data", -1, as_dataframe=True)
                        gaia_df = db.fetch_data("gaia_dr3_data", -1, as_dataframe=True)
                        if confirmed_df.empty and gaia_df.empty:
                            return metrics

                        evaluation_frames = []
                        if not confirmed_df.empty:
                            confirmed_df = confirmed_df.copy()
                            if "is_confirmed_host" not in confirmed_df.columns:
                                confirmed_df["is_confirmed_host"] = 1
                            confirmed_df["is_confirmed_host"] = pd.to_numeric(
                                confirmed_df["is_confirmed_host"], errors="coerce"
                            ).fillna(1).astype(int)
                            evaluation_frames.append(confirmed_df)

                        if not gaia_df.empty:
                            gaia_eval = gaia_df.copy()
                            if "is_confirmed_host" not in gaia_eval.columns:
                                gaia_eval["is_confirmed_host"] = 0
                            gaia_eval["is_confirmed_host"] = pd.to_numeric(
                                gaia_eval["is_confirmed_host"], errors="coerce"
                            ).fillna(0).astype(int)
                            evaluation_frames.append(gaia_eval)

                        eval_df = pd.concat(evaluation_frames, ignore_index=True) if evaluation_frames else pd.DataFrame()
                        if eval_df.empty:
                            return metrics

                        X_eval, y_true = preprocessor.preprocess_gaia_data(
                            eval_df,
                            target_column="is_confirmed_host",
                            default_target=0,
                        )
                        probs = train_result["model"].predict(xgb.DMatrix(X_eval))
                        preds = (probs > 0.5).astype(int)
                        metrics = {
                            "accuracy": float(accuracy_score(y_true, preds)),
                            "precision": float(precision_score(y_true, preds, zero_division=0)),
                            "recall": float(recall_score(y_true, preds, zero_division=0)),
                        }
                    except Exception as exc:
                        logger.log_warning(f"Reinforcement evaluation skipped: {exc}")
                    return metrics

                result = xgboost_trainer.run_reinforcement_training_loop(
                    train_iteration,
                    evaluate_iteration,
                    max_iterations=max_iterations,
                    target_accuracy=target_accuracy,
                    target_precision=target_precision,
                )

                print("Reinforcement training summary:")
                for item in result["history"]:
                    print(f"  iteration {item['iteration']}: accuracy={item['accuracy']:.4f}, precision={item['precision']:.4f}, recall={item['recall']:.4f}")

                if result["achieved"]:
                    print("Target metrics reached.")
                    prompt = input("Run the model on new random data now? [y/N]: ").strip().lower()
                    if prompt in {"y", "yes"}:
                        run_model.run_model()
                        print("Deployment complete. Review predictions and candidate likelihoods in the database.")
                    else:
                        print("Skipped deployment. Use 'deploy' or 'candidates' later.")
                else:
                    print("Target metrics were not reached within the requested iterations. Review the metrics and rerun the command with more iterations.")

            case "candidates" | "likelihoods":
                from data.database.sqlite import db
                limit = int(args[0]) if len(args) > 0 and args[0].isdigit() else 10
                candidates = db.fetch_data("new_exoplanet_candidates", -1, as_dataframe=True)
                if candidates.empty:
                    print("No candidate likelihoods have been stored yet. Run 'deploy' or 'automate-reinforce' first.")
                    return True
                candidates = candidates.sort_values(by="likelihood", ascending=False).head(limit)
                print(f"Top {len(candidates)} candidate likelihoods:")
                for _, row in candidates.iterrows():
                    print(f"  source_id={int(row['source_id'])} likelihood={float(row['likelihood']):.4f}")

            case "settings":
                c = args[0].lower() if args else input("Enter the settings command | regen | : ").strip().lower()
                match c:
                    case "regen":
                        table_name = args[1] if len(args) > 1 else input(
                            "Which table would you like to regenerate? "
                            "(gaia_dr3_data, nasaea_data, test_data, confirmed_exoplanets_data, model_versioning): "
                        ).strip()
                        from data.database.sqlite.db import regenerate_table
                        regenerate_table(table_name)
                

            ## Visualization Commands
            case "visualize":
                print("Visualizing data...")
                # Call the function to visualize data here
                # e.g., visualize_data()
                print("Visualization complete.")

            case _:
                print(f"Unknown command: {command}. Type 'help' for a list of commands.")

    return True


## Starts the CLI to await user commands. This function will run in a loop until
# the user decides to exit.
#
# Updated to use config_manager for configuration management and logging.
def start_cli():

    print(config_manager.get_config_value("welcome_message", "Error: Welcome message not found in config."))
    print("Type 'help' for a list of commands.")
    while True:
        # Supports chained commands separated by ';'
        command_line = input("GaiaML> ")
        chained_commands = [cmd.strip() for cmd in command_line.split(';') if cmd.strip()]

        should_continue = True
        for chained_command in chained_commands:
            should_continue = _execute_command(chained_command)
            if not should_continue:
                break

        if not should_continue:
            break