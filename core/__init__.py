"""WIP"""
from json import dumps

from .connector import Connector
from .metadata import Metadata
from .record import Record


class Project:
    """Project container"""

    def __enter__(self):
        """Enter context"""
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.connector.close()

    def __init__(self, host, path, token):
        """Constructor"""
        self.connector = Connector(host, path, token)
        with self.connector as conn:
            self.metadata = Metadata(
                conn.metadata("export"), conn.field_names("export")
            )

    def records(self, **query):
        """Generates records"""
        with self.connector as conn:
            records = export_content("records", **query)
        while any(records):
            yield Record(records.pop())

    def sql_migration(self, *args, **kwargs):
        """Return SQL migration for project metadata"""
        return self.metadata.sql_migration(*args, **kwargs)

    def sync(self):
        """Update REDCap instance with project alterations"""
        pass


__all__ = ["Connector", "Metadata", "Project"]
