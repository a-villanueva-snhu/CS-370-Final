# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

## Starts the CLI to await user commands. This function will run in a loop until 
# the user decides to exit.
def start_cli():
    print("Welcome to GaiaML CLI!")
    print("Type 'help' for a list of commands.")
    while True:
    ## Handle user input and commands

        command = input("GaiaML> ")
        match command:
            case "exit":
                print("Exiting GaiaML CLI. Goodbye!")
                break
            case "help":
                print("Available commands:")
                print("  help - Show this help message")
                print("  exit - Exit the CLI")
                # Add more commands as needed
            case _:
                print(f"Unknown command: {command}. Type 'help' for a list of commands.")