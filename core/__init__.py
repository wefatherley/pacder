from csv import DictWriter
from logging import getLogger

from .connector import *
from .metadata import *
from .record import *


LOGGER = getLogger(__name__)


class Project:
    """WIP"""

    def __init__(self, host=None, path=None, token=None):
        """Initialize API connector and metadata for a project"""
        if host is None and path is None and token is None:
            self.metadata = Metadata()
        else:
            self.api = Connector(host, path, token)
            with self.api as api:
                self.metadata = Metadata(
                    api.metadata("export"), api.field_names("export")
                )
