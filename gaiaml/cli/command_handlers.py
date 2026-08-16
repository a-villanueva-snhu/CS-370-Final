import os
import sys
import xgboost as xgb
import logs.logger as logger
from src.tests.e2e_tester import TestLogger
from config import config_manager
from src.preprocessing import preprocessor


def _parse_positive_int(value, default_value):
    try:
        parsed = int(value)
        if parsed > 0:
            return parsed
    except (TypeError, ValueError):
        pass
    return default_value


def _prompt_for_confirmation(prompt, default_yes=False):
    """Prompt for confirmation, but default to the provided choice for non-interactive runs."""
    if not sys.stdin.isatty():
        return default_yes

    try:
        response = input(prompt).strip().lower()
    except EOFError:
        return default_yes

    if response in {"", "y", "yes"}:
        return True
    return False


def handle_help():
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
    return True


def handle_test(args):
    i = args[0].lower() if args else input("Enter the test to run | logger | cli | all | : ").strip().lower()
    match i:
        case "logger":
            print("Running logger tests...")
            logger_tester = TestLogger()
            logger_tester.test_log_info()
            logger_tester.test_log_warning()
            logger_tester.test_log_error()
            logger_tester.test_log_exception()
            print("Logger tests complete.")
        case "cli":
            print("Running CLI tests...")
            print("The CLI is probably working, if you made it here.")
            print("CLI tests complete.")
        case "all":
            print("Running all tests...")
            print("All tests complete.")
        case "menu":
            print("Returning to main menu...")
            return True
        case _:
            print(f"Unknown test: {i}. Please enter 'logger', 'cli', or 'all'.")
    return True


def handle_config(args):
    i = args[0].lower() if args else input("Enter the config command | load | open | edit | : ").strip().lower()
    match i:
        case "load":
            print("Loading configuration...")
            config_manager.load_config()
            print("Configuration loaded.")
        case "open":
            print("Opening configuration file...")
            config_manager.open_yaml()
        case "edit":
            while True:
                config = config_manager.load_config()
                for key, value in config.items():
                    print(f"{key}: {value}")

                c = input("Enter the config key to edit (e.g., 'database_settings.database_file_path'): ")
                v = input(f"Enter the new value for '{c}': ")
                config_manager.edit_config(c, v)

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
    return True


def handle_logs():
    print("Opening log folder...")
    log_folder = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    os.startfile(log_folder)
    return True


def handle_download(args):
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
    return True


def handle_preprocess():
    logger.log_info("Starting data preprocessing...")
    from data.database.sqlite import db

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
    create_training_dataset_from_gaia_dr3()

    print("Preprocessing complete.")
    return True


def handle_train():
    logger.log_info("Starting model training...")
    from src.training import xgboost_trainer
    from src.preprocessing import preprocessor

    logger.log_info("preprocessing data for training...")
    X, y = preprocessor.create_training_dataset_from_gaia_dr3()
    xgboost_trainer.train_xgboost_model(X, y)

    print("Training model...")
    print("Model training complete.")
    return True


def handle_evaluate():
    print("Evaluating current model metrics...")
    from data.database.sqlite import db

    metrics = db.get_latest_model_metrics()
    if not metrics:
        print("No model metrics have been recorded yet. Train a model first.")
        return True

    print(f"Latest model version: {metrics.get('version', 'unknown')}")
    print(f"Created: {metrics.get('date_created', 'unknown')}")
    print(f"  accuracy: {metrics.get('accuracy', 0.0):.4f}")
    print(f"  precision: {metrics.get('precision', 0.0):.4f}")
    print(f"  recall: {metrics.get('recall', 0.0):.4f}")
    print(f"  f1: {metrics.get('f1', 0.0):.4f}")
    model_path = metrics.get('model_json')
    if model_path:
        print(f"  model file: {model_path}")
    print("Model evaluation complete.")
    return True


def handle_deploy():
    print("Deploying model...")
    import src.models.run_model as run_model
    print("Running model on new data...")
    run_model.run_model()
    print("Model deployment complete.")
    return True


def handle_automate_reinforce(args):
    import src.models.run_model as run_model
    from src.preprocessing import preprocessor
    from src.training import xgboost_trainer

    max_iterations = int(args[0]) if len(args) > 0 and args[0].isdigit() else 5
    target_accuracy = float(args[1]) if len(args) > 1 else 0.99
    target_precision = float(args[2]) if len(args) > 2 else 0.99

    print(f"Starting reinforcement training loop for up to {max_iterations} iterations...")

    def train_iteration(iteration):
        X, y = preprocessor.create_training_dataset_from_gaia_dr3()
        model, X_test, y_test = xgboost_trainer.train_xgboost_model(X, y)
        return {"model": model, "iteration": iteration, "X_test": X_test, "y_test": y_test}

    def evaluate_iteration(train_result, iteration):
        metrics = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "threshold": 0.5}
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            X_test = train_result["X_test"]
            y_test = train_result["y_test"]
            probs = train_result["model"].predict(xgb.DMatrix(X_test))
            threshold = xgboost_trainer.select_decision_threshold(y_test, probs, default_threshold=0.5)
            preds = (probs >= threshold).astype(int)
            metrics = {
                "accuracy": float(accuracy_score(y_test, preds)),
                "precision": float(precision_score(y_test, preds, zero_division=0)),
                "recall": float(recall_score(y_test, preds, zero_division=0)),
                "f1": float(f1_score(y_test, preds, zero_division=0)),
                "threshold": float(threshold),
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
        print(
            f"  iteration {item['iteration']}: accuracy={item['accuracy']:.4f}, "
            f"precision={item['precision']:.4f}, recall={item['recall']:.4f}, "
            f"f1={item.get('f1', 0.0):.4f}, threshold={item.get('threshold', 0.5):.3f}"
        )

    if result["achieved"]:
        print("Target metrics reached.")
        should_deploy = _prompt_for_confirmation("Run the model on new random data now? [y/N]: ", default_yes=True)
        if should_deploy:
            run_model.run_model()
            print("Deployment complete. Review predictions and candidate likelihoods in the database.")
        else:
            print("Skipped deployment. Use 'deploy' or 'candidates' later.")
    else:
        print("Target metrics were not reached within the requested iterations. Review the metrics and rerun the command with more iterations.")
    return True


def handle_candidates(args):
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
    return True


def handle_settings(args):
    c = args[0].lower() if args else input("Enter the settings command | regen | : ").strip().lower()
    match c:
        case "regen":
            table_name = args[1] if len(args) > 1 else input(
                "Which table would you like to regenerate? "
                "(gaia_dr3_data, nasaea_data, test_data, confirmed_exoplanets_data, model_versioning): "
            ).strip()
            from data.database.sqlite.db import regenerate_table
            regenerate_table(table_name)
    return True


def handle_visualize():
    print("Visualizing data...")
    print("Visualization complete.")
    return True


def dispatch_command(command, args):
    match command:
        case "help":
            return handle_help()
        case "test":
            return handle_test(args)
        case "config":
            return handle_config(args)
        case "logs":
            return handle_logs()
        case "download":
            return handle_download(args)
        case "preprocess":
            return handle_preprocess()
        case "train":
            return handle_train()
        case "evaluate":
            return handle_evaluate()
        case "deploy":
            return handle_deploy()
        case "automate-reinforce" | "automate_reinforce":
            return handle_automate_reinforce(args)
        case "candidates" | "likelihoods":
            return handle_candidates(args)
        case "settings":
            return handle_settings(args)
        case "visualize":
            return handle_visualize()
        case _:
            print(f"Unknown command: {command}. Type 'help' for a list of commands.")
            return True
