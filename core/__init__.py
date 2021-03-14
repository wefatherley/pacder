"""WIP"""
from .connector import Connector
from .metadata import Metadata


class Project:
    """Project container"""

    def __init__(self, host, path, token):
        """Constructor"""
        self.connector = Connector(host, path, token)
        with self.connector as conn:
            self.metadata = Metadata(
                conn.metadata("export"),
                conn.field_names("export")
            )
        self.sql_migration = self.metadata.sql_migration

    def update_metadata(self, metadatum):
        """Updates project metadata"""
        pass

    def records(self, **query):
        """Generates records"""

__all__ = ["Connector", "Metadata", "Project"]
