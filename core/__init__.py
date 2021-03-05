from collections import namedtuple
from logging import getLogger

from .connector import Connector
from .metadata import Metadata


LOGGER = getLogger(__name__)


Datum = namedtuple("Datum", ["original_field_name", "value", "logic"])


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
        
    def records(self, key=None, **query):
        """Generate records"""
        with self.api as api:
            records = api.records("export", **query)
        if key is not None:
            records.sort(key=key)
        while any(records):
            record = self.metadata.load_record(records.pop())
            for key in record.keys():
                record[key] = Datum(
                    self.metadata.raw_field_names[
                        key
                    ]["original_field_name"],
                    record[key],
                    self.metadata[key]["branching_logic"](record)
                )
            yield record


__all__ = ["Connector", "Metadata", "Project",]
