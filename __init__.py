"""pacder"""
from json import loads
from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .record import Record


__all__ = ["Connector", "Metadata", "Project", "Record",]


LOGGER = getLogger(__name__)


class Project:
    """Project container"""

    def __delitem__(self, key):
        """"""
        pass

    def __enter__(self):
        """Enter context"""
        if self.connector.sock is None:
            self.connector.connect()
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.metadata.push()
        self.connector.close()

    def __getitem__(self, key):
        """"""
        pass

    def __init__(self, host, path, token):
        """Constructor"""
        self.connector = Connector(host, path, token)
        with self.connector as conn:
            self.metadata = Metadata(
                loads(conn.metadata("export")),
                loads(conn.field_names("export")),
                project=self
            )

    def __setitem__(self, key, value):
        """"""
        pass
