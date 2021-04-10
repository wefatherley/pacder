"""pacder"""
from json import loads
from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .record import Record


LOGGER = getLogger(__name__)


class Project:
    """Project container"""

    def __enter__(self):
        """Enter context"""
        if self.connector.sock is None:
            self.connector.connect()
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.metadata.push()
        self.connector.close()

    def __init__(self, host, path, token):
        """Constructor"""
        self.connector = Connector(host, path, token)
        with self.connector as conn:
            self.metadata = Metadata(
                conn.metadata("export"), conn.field_names("export")
            )

    def iter_records(self, **query):
        """Yield Record instances that match query"""
        with self.connector as conn:
            records = loads(
                export_content("records", **query).decode("latin-1")
            )
        while any(records):
            yield Record(records.pop())

    def sql_migration(self, *args, **kwargs):
        """Return SQL migration for project metadata"""
        return self.metadata.sql_migration(*args, **kwargs)


__all__ = ["Connector", "Metadata", "Project"]
