import os
import sys
from argparse import ArgumentParser
from importlib import import_module
from pkgutil import iter_modules

from ace import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    base_path = os.path.dirname(__file__)
    commands = load_commands(base_path)

    parser = create_parser()
    add_subparsers(parser, commands)
    args = vars(parser.parse_args())

    action = args.pop('command')
    if action and action in commands:
        commands[action].handle(**args)
    else:
        parser.print_help()


def load_commands(path):
    """Loads commands package form given path.

    Args:
        path (str): Path to load commands package.

    Returns:
        dict: Dictionary of command name and instance pairs.

    """
    commands = {}

    for _, name, is_pkg in iter_modules([os.path.join(path, 'commands')]):
        if not is_pkg and not name.startswith('_') and name != 'base':
            module = import_module('ace.commands.{}'.format(name))
            commands[name] = module.Command()

    return commands


def create_parser():
    """Creates the root command line argument parser.

    Returns:
        argparse.ArgumentParser: Created root command line argument parser.

    """
    parser = ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description='CLI for Amiga C Engine'
    )

    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.set_defaults()

    return parser


def add_subparsers(parser, commands):
    """Adds commands arguments to given command line argument parser.

    Args:
        parser (argparse.ArgumentParser): Root command line argument parser.
        commands (dict): Command collection.

    """
    subparsers = parser.add_subparsers(
        help='available subcommands:',
        metavar='<command>',
        dest='command'
    )

    for name, command in commands.items():
        command.add_parser(name, subparsers)
