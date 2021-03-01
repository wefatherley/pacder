from argparse import ArgumentParser
from logging import basicConfig, INFO, getLogger, WARN
from os import environ
from sys import exit


from . import Project


basicConfig(
    format="%(asctime)s - %(name)s - %(message)s",
    level=INFO
)


parser = ArgumentParser(prog="redcapp")
parser.add_argument(
    "command", choices=["run", "test"], help="Run or test services"
)
parser.add_argument(
    "--env",
    action="store_true",
    help="Signals to gather host, path, token from environment"
)
args = parser.parse_args()


if args.command == "run":
    if args.env:
        host = environ.get("REDCAP_API_HOST")
        path = environ.get("REDCAP_API_PATH")
        token = environ.get("REDCAP_API_TOKEN")
        if not all((host, path, token)):
            exit("Environment is missing host or path or token")
    else:
        environ["REDCAP_API_HOST"] = input("Enter API host: ")
        environ["REDCAP_API_PATH"] = input("Enter API path: ")
        environ["REDCAP_API_TOKEN"] = input("Enter project API token: ")
    try:
        while True:
            input("??? ")
    except (EOFError, KeyboardInterrupt):
        exit("Session interrupted")

elif args.command == "test":
    pass
