"""Record and related objects"""
from logging import getLogger

from .util import data_type_map


LOGGER = getLogger(__name__)


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
        if self.metadata[key]["field_type"] == "checkbox":
            checkboxes = {
                k.split("___")[-1]: True if v else False
                for k,v in self.items.items()
                if k.startswith(ofn + "___")
            }
        else:
            valid = (
                self.metadata[key]["text_validation_min"](data)
                and self.metadata[key]["text_validation_max"](data)
            )
            value = data_type_map[
                self.metadata[key][self.metadata.columns[7]]
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
        return record_datum

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
        self.items[key] = value
        