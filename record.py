"""Record and related objects"""
from collections import namedtuple
from logging import getLogger

from .metadata import Metadata
from .util import data_type_map


__all__ = ["Record",]


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


class RecordDep:
    """Record container"""

    def __contains__(self, item):
        """Implement membership test operators"""
        pass

    def __getitem__(self, key):
        """Get lazily-casted data"""
        # TODO: the project should actually do all this stuff
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
            raise Exception("field not in project metadata")
        self.items[key] = value
        

class Field:
    """Field descriptor"""

    def __delete__(self, obj):
        """Validate delete and delete field value"""
        return getattr(
            self, "del_" + obj.metadata[self.name]["field_type"]
        )(obj.metadata, obj.record_json[self.name])

    def __get__(self, obj, obj_owner=None):
        """Validate and return field value"""
        return getattr(
            self, "get_" + obj.metadata[self.name]["field_type"]
        )(obj.metadata, obj.record_json[self.name])

    def __set__(self, obj, value):
        """Validate and set field value"""
        # two situations:
        # empty record, setting for the first time
        # or updating set value
        return getattr(
            self, "set_" + obj.metadata[self.name]["field_type"]
        )(obj.metadata, obj.record_json[self.name])

    def __set_name__(self, obj, name):
        """Remember what descriptor manages"""
        self.name = name

    def del_text(self, metadata, value): pass
    def del_notes(self, metadata, value): pass
    def del_dropdown(self, metadata, value): pass
    def del_radio(self, metadata, value): pass
    def del_checkbox(self, metadata, value): pass
    def del_file(self, metadata, value): pass
    def del_calc(self, metadata, value): pass
    def del_sql(self, metadata, value): pass
    def del_descriptive(self, metadata, value): pass
    def del_slider(self, metadata, value): pass
    def del_yesno(self, metadata, value): pass
    def del_truefalse(self, metadata, value): pass

    def get_text(self, metadata, value): pass
    def get_notes(self, metadata, value): pass
    def get_dropdown(self, metadata, value): pass
    def get_radio(self, metadata, value): pass
    def get_checkbox(self, metadata, value): pass
    def get_file(self, metadata, value): pass
    def get_calc(self, metadata, value): pass
    def get_sql(self, metadata, value): pass
    def get_descriptive(self, metadata, value): pass
    def get_slider(self, metadata, value): pass
    def get_yesno(self, metadata, value): pass
    def get_truefalse(self, metadata, value): pass

    def set_text(self, metadata, value): pass
    def set_notes(self, metadata, value): pass
    def set_dropdown(self, metadata, value): pass
    def set_radio(self, metadata, value): pass
    def set_checkbox(self, metadata, value): pass
    def set_file(self, metadata, value): pass
    def set_calc(self, metadata, value): pass
    def set_sql(self, metadata, value): pass
    def set_descriptive(self, metadata, value): pass
    def set_slider(self, metadata, value): pass
    def set_yesno(self, metadata, value): pass
    def set_truefalse(self, metadata, value): pass


class Record:
    """REDCap record container"""

    # def __call__(self, raw_record):
    #     """(re)set record data values"""
    #     for k,v in raw_record.items():
    #         if "___" in k:
    #             k = k.split("___")
    #             k,v = k[0], (k[1], v)
    #         setattr(self, k, v)
    
    def __contains__(self, item):
        """Implement membership test operator"""
        pass

    def __delitem__(self, field):
        """Delete field value"""
        pass
    
    def __eq__(self, item):
        """Implement equality comparison operator"""
        pass

    def __getitem__(self, field):
        """Return field"""
        return getattr(self, field)

    def __init__(self, record_json=dict(), **kwargs):
        """Construct instance"""
        if isinstance(record_json, (bytes, str)):
            record_json = loads(record_json)
        self.record_json = record_json

    def __iter__(self):
        """return iterator of self"""
        pass

    def __len__(self):
        """Return number of fields"""
        pass

    def __new__(cls, **kwargs):
        """Initialize and name field descriptors"""
        try:
            metadata = kwargs["metadata"]
        except KeyError:
            raise Exception("Record class requires metadata")
        else:
            if not isinstance(metadata, Metadata):
                raise Exception("metadata must be Metadata instance")
            for md in metadata:
                setattr(cls, md["field_name"], FieldType())
            obj = super().__new__(cls)
            obj.metadata = metadata
            return obj

    def __setitem__(self, field, value):
        """Set record field value"""
        setattr(self, field, value)
    
    
    def preprocessor(self, func):
        """Validation function wrapper"""
        pass
