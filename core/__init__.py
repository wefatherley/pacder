from csv import DictWriter
from logging import getLogger

from .connector import *
from .metadata import *


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

    def export_resource(self, resource, path=None, **parameters):
        """WIP"""
        if not hasattr(self, "api"):
            raise NotImplementedError("No API connector")
        with self.api as api:
            if resource == "record":
                data = getattr(api, resource)("export", **parameters)
                if path is None:
                    return self.metadata.load_record(data)
                else:
                    with open(path, "w", newline="") as fp:
                        writer = DictWriter(fp, fieldnames=COLUMNS)
                        writer.writeheader()
                        for record in data:
                            writer.write(record)

    def import_resource(self, resource, data, **parameters):
        """WIP"""
        if not hasattr(self, "api"):
            raise NotImplementedError("No API connector")
        pass

    def delete_resource(self, resource, data, **parameters):
        """WIP"""
        if not hasattr(self, "api"):
            raise NotImplementedError("No API connector")
        pass
