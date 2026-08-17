# This is the command line interface (CLI) for GaiaML. 
# It handles user input and output, and provides a way to 
# interact with the application.

import os
import shlex
import sys
import logs.logger as logger
from config import config_manager
from cli.command_handlers import dispatch_command
# from src.utils import gaia_downloader  ## Moved to lazy load in command handling to avoid load time issues with sqlite and astroquery. These modules are not needed for the CLI to start, and can be loaded when needed.


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

    if command in {"exit", "quit", "q", "e"}:
        print("Exiting GaiaML CLI. Goodbye!")
        return False

    return dispatch_command(command, args)


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