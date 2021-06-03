"""Record and related objects"""
from collections import namedtuple
from json import loads
from logging import getLogger

from .util import data_type_map


__all__ = ["Record",]


LOGGER = getLogger(__name__)


class Field:
    """field descriptor"""

    def __delete__(self, obj):
        """validate delete and delete field value"""
        setattr(obj, "_" + self.name, None)

    def __get__(self, obj, obj_owner=None):
        """validate and return field value"""
        return getattr(obj, "_" + self.name, None)

    def __set__(self, obj, value):
        """cast and set field value"""
        value = data_type_map[
            obj.project.metadata[self.name][
                obj.project.metadata.columns[7]
            ]
        ][0](value)
        setattr(obj, "_" + self.name, value)

    def __set_name__(self, obj_owner, name):
        """remember what field this descriptor manages"""
        self.name = name


class Record:
    """REDCap record container"""
    
    def __contains__(self, field):
        """implement membership test operator"""
        if field in self.project.metadata.raw_field_names:
            return True
        return False

    def __delitem__(self, field):
        """delete field value"""
        if field not in self.project.metadata.raw_field_names:
            raise Exception("field not valid")
        setattr(self, field, None)
    
    def __eq__(self, other):
        """implement `==`"""
        if type(self) is not type(other):
            return NotImplemented
        if hasattr(other, "record_json"):
            if other.record_json == self.record_json:
                return True
        return False

    def __getitem__(self, field):
        """return field"""
        return getattr(self, field)

    def __init__(self, **kwargs):
        """construct instance"""
        record_json = kwargs.get("record_json")
        if record_json is not None:
            if isinstance(record_json, (bytes, str)):
                record_json = loads(record_json)
            for k,v in record_json.items():
                setattr(self, k, v)
        else:
            for field in self.project.metadata.raw_field_names:
                setattr(self, field, None)

    def __iter__(self):
        """return iterator of self"""
        return (
            self[field] for field
            in self.project.metadata.raw_field_names
        )

    def __len__(self):
        """return number of fields"""
        return len(self.record_json)

    def __new__(cls, **kwargs):
        """initialize and name field descriptors"""
        obj = super().__new__(cls)
        obj.project = kwargs.get("project")
        for field in obj.project.metadata.raw_field_names:
            setattr(obj, field, Field())
        return obj

    def __setitem__(self, field, value):
        """set record field value"""
        if field not in self.project.metadata.raw_field_names:
            raise Exception("field not valid")
        setattr(self, field, value)
