"""Record and related objects"""
from logging import getLogger

from .util import data_type_map


LOGGER = getLogger(__name__)


TVTOSSN = "text_validation_type_or_show_slider_number"


RecordDatum = namedtuple(
    "RecordDatum",
    [
        "branching_logic",
        "ofn",
        "raw_value",
        "valid",
        "value",
        "values"
    ]
)


class Record:
    """Record container"""

    def __contains__(self, item):
        """Implement membership test operators"""
        pass

    def __getitem__(self, key):
        """Get lazily-casted data"""
        data = self.items[key]
        if isinstance(data, RecordDatum):
            return data
        ofn = self.metadata[key]["field_name"]
        valid = (
            self.metadata[key]["text_validation_min"](data)
            and self.metadata[key]["text_validation_max"](data)
        )
        if self.metadata[key]["field_type"] == "checkbox":
            if "___" in key:
                pass
            else:
                pass
        else:
            value = data_type_map[
                self.metadata[key][TVTOSSN]
            ][0](data)
            values = [data]
            record_datum = RecordDatum(
                branching_logic=self.metadata[key][
                    "branching_logic"
                ](record),
                ofn=ofn,
                raw_value=raw_value,
                valid=valid,
                value=value,
                values=values
            )
            self.items[key] = record_datum
            return record_datum
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

    def __init__(self, raw_record, **kwargs):
        """Construct record"""
        self.items = raw_record
        if "metadata" in kwargs:
            self.metadata = kwargs["metadata"]
        else:
            self.metadata = dict()
            LOGGER.warn("Record has no metadata")

    def __setitem__(self, key, value):
        """Set record item"""
        if key not in self.metadata.raw_field_names:
            raise Exception("Field not in project metadata")
