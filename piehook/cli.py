import argparse
import sys
import os

from piehook.hooks import hooks

class Command:
    def __init__(self, name, help):
        self.name = name
        self.help = help

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        pass


class CreateCommand(Command):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("name", type=str, help="The name of the hooks file to create (without suffix).")
        parser.add_argument("-d", "--directory", help="The directory to create the hooks file in.")
        parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output.")

    def handle(self, args):
        abs_path = os.path.abspath(args.directory or os.getcwd())
        self._create_hooks_file(abs_path, args.name)

    def _create_hooks_file(self, dir, name):
        if not '_hooks' in name:
            name += '_hooks'
        
        if not name.endswith(".py"):
            name += ".py"
        
        if not os.path.exists(dir):
            os.makedirs(dir)

        full_path = os.path.join(dir, name)

        with open(full_path, 'w') as f:
            f.write("""
from piehook.hooks import hooks 
                    
@hooks.add("my_hook")
def my_hook():
    print("Hello from my_hook!")
                    """
                    )


class RunCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("id", type=str, help="ID of the hook to run")
        parser.add_argument("-p", "--path", help="The root path for hook discovery.")
        parser.add_argument("-s", "--suffix", help="The file suffix for hook discovery (without .py).")
        parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output.")

    def handle(self, args):
        suffix = args.suffix or '_hooks'
        hooks.set_verbose(args.verbose)
        hooks.import_hooks(root_path=args.path, file_suffix=suffix)
        hooks.run(args.id)


class CLI:
    """
    A command-line interface class that allows for the addition of sub-commands and their corresponding arguments.

    Attributes:
    - description (str): A brief description of the CLI.
    - parser (argparse.ArgumentParser): An ArgumentParser object that handles parsing of command-line arguments.
    - subparsers (argparse._SubParsersAction): A sub-parser object that handles sub-commands.
    - commands (dict): A dictionary that maps command names to their corresponding Command objects.
    """

    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)
        self.subparsers = self.parser.add_subparsers(dest="command", help="Sub-command help")
        self.commands = {}

    def add_command(self, command):
        """
        Adds a sub-command to the CLI.

        Args:
        - command (Command): A Command object representing the sub-command to be added.
        """
        parser = self.subparsers.add_parser(command.name, help=command.help)
        command.add_arguments(parser)
        parser.set_defaults(func=command.handle)
        self.commands[command.name] = command

    def run(self):
        """
        Parses command-line arguments and executes the corresponding sub-command.
        """
        args = self.parser.parse_args()
        if args.command is None:
            self.parser.print_help()
            sys.exit(1)
        args.func(args)


def main():
    cli = CLI(description="A simple hook system for Python.")
    cli.add_command(CreateCommand("create", "Create a new hook"))
    cli.add_command(RunCommand("run", "Run a hook"))
    cli.run()
    

if __name__ == "__main__":
    main()