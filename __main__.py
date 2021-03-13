"""WIP Main"""
from argparse import ArgumentParser
from http import server, HTTPStatus
from logging import basicConfig, getLogger, INFO
from sys import exit

from . import Project, Service


parser = ArgumentParser(prog="redcapp")
parser.add_argument(
    "command", choices=["run", "test"], help="Run or test services"
)
args = parser.parse_args()


if args.command == "run":

    # initialize logging
    basicConfig(
        filename="service.log",
        format="127.0.0.1 - - [%(asctime)s] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        level=INFO
    )
    LOGGER = getLogger(__name__)

    # spin up service
    try:
        service = server.ThreadingHTTPServer(
            ("127.0.0.1", 8080), Service
        )
        LOGGER.info("listening on loopback, port 8080")
        service.serve_forever()
    except (EOFError, KeyboardInterrupt):
        service.shutdown()
        LOGGER.info("shut down successful")
        exit()
        

elif args.command == "test":
    pass