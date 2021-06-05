"""pacder"""
from json import loads
from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .record import Record


__all__ = ["Connector", "Metadata", "Project", "Record",]


LOGGER = getLogger(__name__)


class Project:
    """container for REDCap project"""

    def __delitem__(self, key):
        """remove (delete) project resource"""
        pass

    def __enter__(self):
        """enter context"""
        if self.connector.sock is None:
            self.connector.connect()
        return self

    def __exit__(self, typ, val, trb):
        """exit context"""
        self.connector.close()

    def __getitem__(self, key):
        """fetch (export) project resource"""
        pass

    def __init__(self, host, path, token):
        """constructor"""
        self.connector = Connector(host, path, token)
        self.metadata = Metadata(project=self)

    def __setitem__(self, key, value):
        """send (import) project resource"""
        pass
