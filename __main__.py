"""CLI entrypoint"""
from argparse import Action, ArgumentParser
from logging import getLogger

from . import *


LOGGER = getLogger(__name__)


class Project(Action):
    """Identify project for subsequent flags"""

    def __init__(self, *args, **kwargs):
        """Construct project action"""
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        """Interact with projects"""
        pass


parser = ArgumentParser(prog="pacder")
parser.add_argument("project", action=Project, nargs="*")


"""
pacder project -i records
"""
