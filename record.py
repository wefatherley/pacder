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
        if field in self.project.metadata:
            return True
        return False

    def __delitem__(self, field):
        """delete field value"""
        if field not in self.project.metadata:
            raise Exception("no such field")
        setattr(self, field, None)
    
    def __eq__(self, other):
        """implement equality test operator"""
        if type(self) is not type(other):
            return NotImplemented
        if all(
            self.get(field) == other.get(field)
            for field in self.project.metadata
        ):
            return True
        return False

    def __getitem__(self, field):
        """return field"""
        if field not in self.project.metadata:
            raise Exception("no such field")
        return getattr(self, field)

    def __init__(self, raw_record):
        """construct instance"""
        for k,v in raw_record.items():
            if k in self.project.metadata:
                setattr(self, k, v)
            else:
                raise Exception("raw record doesn't match metadata")

    def __iter__(self):
        """return iterator of self"""
        return (self[field] for field in self.project.metadata)

    def __len__(self):
        """return number of fields"""
        return len(self.project.metadata)

    def __new__(cls, **kwargs):
        """initialize and name field descriptors"""
        obj = super().__new__(cls)
        obj.project = kwargs.get("project")
        for field in obj.project.metadata:
            setattr(obj, field, Field())
        return obj

    def __setitem__(self, field, value):
        """set record field value"""
        if field not in self.project.metadata:
            raise Exception("no such field")
        setattr(self, field, value)
