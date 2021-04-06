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


class Record(dict):
    """Record container"""

    def __init__(self, raw_record, **kwargs):
        """Construct record"""
        if "metadata" not in kwargs:
            raise Exception("Record needs metadata")
        super().__init__()
        self.metadata = kwargs["metadata"]
        self.raw_record = raw_record
        checkboxes = dict()
        for k,v in self.raw_record.items():
            if self.metadata[k]["field_type"] == "checkbox":
                ofn, choice = k.split("___")
                v = True if v else False
                try: checkboxes[ofn][choice] = v
                except KeyError: checkboxes[ofn] = {choice: v}
            else:
                branching_logic = self.metadata[k][
                    "branching_logic"
                ](raw_record)
                valid = (
                    self.metadata[k]["text_validation_min"](v)
                    and self.metadata[k]["text_validation_max"](v)
                )
                if self.metadata[k]["required_filed"]:
                    valid = valid and v
                typed_v = data_type_map[
                    self.metadata[k][self.metadata.columns[7]]
                ][0](v)
                self[k] = RecordDatum(
                    branching_logic=branching_logic,
                    ofn=k,
                    raw_value=v,
                    valid=valid,
                    value=typed_v,
                    values=None
                )
        for k,v in checkboxes.items():
            branching_logic = self.metadata[k][
                "branching_logic"
            ](raw_record)
            value = any(v.values())
            valid = True
            if branching_logic and not value:
                valid = False
            self[k] = RecordDatum(
                branching_logic=branching_logic,
                ofn=k,
                raw_value=None,
                valid=valid,
                value=value,
                values=v
            )

    def __setitem__(self, key, value):
        """Set record item"""
        if key not in self.metadata.raw_field_names:
            raise Exception("Field not in project metadata")
        super().__setitem__(key, value)
