"""pacder"""
from json import loads
from logging import getLogger

from .connector import Connector
from .metadata import Metadata
from .util import RecordDatum


LOGGER = getLogger(__name__)
TVTOSSN = "text_validation_type_or_show_slider_number"


class Project:
    """Project container"""

    def __enter__(self):
        """Enter context"""
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.sync()
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
        query["format"] = "json"
        with self.connector as conn:
            records = loads(
                export_content("records", **query).decode("latin-1")
            )
        while any(records):
            checkboxes = dict()
            record = records.pop()
            for key in record.keys():
                ofn = self.metadata[key]["field_name"]
                raw_value = record[key]
                valid = (
                    self.metadata[key][
                        "text_validation_min"
                    ](raw_value)
                    and self.metadata[key][
                        "text_validation_max"
                    ](raw_value)
                )
                if self.metadata[key]["field_type"] == "checkbox":
                    subkey = key.split("___")[-1]
                    try:
                        checkboxes[ofn][subkey] = record[key]
                    except KeyError:
                        checkboxes[ofn] = {subkey: record[key]}
                else:
                    value = data_type_map[
                        self.metadata[key][TVTOSSN]
                    ][0](record[key])
                    values = [value]
                    record[key] = RecordDatum(
                        branching_logic=self.metadata[key][
                            "branching_logic"
                        ](record),
                        ofn=ofn,
                        raw_value=raw_value,
                        valid=valid,
                        value=value,
                        values=values
                    )
            for k,vals in checkboxes.items():
                bl = self.metadata[k]["branching_logic"](record)
                atleastone = any(vals.values())
                valid = not (atleastone and not bl) # WIP
                record[k] = RecordDatum(
                    branching_logic=bl,
                    ofn=ofn,
                    raw_value=vals,
                    valid=valid,
                    value=atleastone,
                    values={k: bool(v) for k,v in vals.items()}
                )
            yield record

    def sql_migration(self, *args, **kwargs):
        """Return SQL migration for project metadata"""
        return self.metadata.sql_migration(*args, **kwargs)

    def sync(self):
        """Import project changes"""
        raise NotImplementedError


__all__ = ["Connector", "Metadata", "Project"]
