"""pacder"""
from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .util import RecordDatum


LOGGER = getLogger(__name__)


class BaseProject:
    pass


class Project:
    """Project container"""

    def __enter__(self):
        """Enter context"""
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.connector.close()
        # TODO: sync changes with redcap instance

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
            record = records.pop()
            for key in record.keys():
                branching_logic = self.metadata[key][
                    "branching_logic"
                ](record)
                ofn = self.metadata[key]["field_name"]
                raw_value = record[key]
                valid = (
                    self.metadata[key][
                        "text_validation_min"
                    ](record[key])
                    and self.metadata[key][
                        "text_validation_max"
                    ](record[key])
                )
                value = data_type_map[
                    self.metadata[
                        "text_validation_type_or_show_slider_number"
                    ][key]
                ][0](record[key])
                values = None
                record[key] = RecordDatum(
                    branching_logic=branching_logic,
                    ofn=ofn,
                    raw_value=raw_value,
                    valid=valid,
                    value=value,
                    values=values
                )
            yield record

    def sql_migration(self, *args, **kwargs):
        """Return SQL migration for project metadata"""
        return self.metadata.sql_migration(*args, **kwargs)


__all__ = ["Connector", "Metadata", "Project"]
