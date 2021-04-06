"""CLI entrypoint"""
from argparse import Action, ArgumentParser
from base64 import b64decode, b64encode
from logging import getLogger
from os import environ, getcwd, listdir, makedirs
from unittest import mock, TestLoader

from . import *
from .test import test_suite, test_runner


LOGGER = getLogger(__name__)        


parser = ArgumentParser(prog="pacder")
parser.add_argument(
    "command", choices=["delete", "export", "import", "init", "test"]
)
parser.add_argument(
    "content", choices=[
        "arms", "events", "field_names", "files", "instruments",
        "metadata", "projects", "records", "repeating_ie", "reports",
        "redcap", "surveys", "users", "null"
    ],
    default="null",
    nargs="?"
)
args = parser.parse_args()


# main
if args.command == "test":
    test_runner.run(test_suite)
elif args.command == "init":
    try:
        home = environ["HOME"]
    except KeyError:
        home = getcwd()
    if (
        ".config" not in listdir(home)
        or "pacder" not in listdir(home + "/.config")
    ):
        makedirs(home + "/.config/pacder", mode=0o740)
    