from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .record import Record


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
        
    def records(self, **query):
        """Generator of redcapp record instances"""
        with self.api as api:
            records_json = api.records("export", **query)
            while len(records) != 0:
                yield Record(records.pop())


__all__ = ["Connector", "Metadata", "Project", "Record",]
