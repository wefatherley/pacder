"""WIP"""
from io import StringIO
from json import dump

from .connector import Connector
from .metadata import Metadata


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
                conn.metadata("export"), conn.field_names("export"))

    def records(self, **query):
        """Generates records"""
        with self.connector as conn:
            records = export_content("records", **query)
        while any(records):
            yield self.metadata.load_record(records.pop())

    def sql_migration(self, *args, **kwargs):
        """Return SQL migration for project metadata"""
        return self.metadata.sql_migration(*args, **kwargs)

    def update_metadata(self, metadatum):
        """Updates project metadata"""
        if not isinstance(metadatum, dict):
            raise Exception("Metadatum must be a dictionary")
        if list(metadatum.keys) != self.metadata.columns:
            raise Exception("Metadatum must have metadata columns")
        fp = StringIO()
        dump(self.metadata.raw_metadata + [metadatum], fp)
        with self.connector as conn:
            conn.import_content("metadata", fp)


__all__ = ["Connector", "Metadata", "Project"]
