"""Record objects"""
from logging import getLogger

from .util import data_type_map


LOGGER = getLogger(__name__)


TVTOSSN = "text_validation_type_or_show_slider_number"


class Record:
    """Record object"""

    def __delitem__(self, key):
        """Delete record datum"""
        if key not in self.raw_record:
            raise KeyError
        del self.raw_record[key]
        try: del self.items[key]
        except KeyError: return

    def __getitem__(self, key):
        """Get record datum"""
        if key not in self.raw_record:
            raise KeyError
        try:
            return self.items[key]
        except KeyError:
            if self.metadata[key][TVTOSSN] == "checkbox":
                if "___" in key:
                    pass
                    
    def __init__(self, raw_record, metadata):
        """Record constructor"""
        self.items = dict()
        self.metadata = metadata
        self.raw_record = raw_record

    def __len__(self):
        return len(self.raw_record)

    def __setitem__(self, key, value):
        """Set record datum"""
        if key in self.metadata:
            if isinstance(value, str):
                self.raw_record[key] = value
            else:
                self.raw_record[key] = data_type_map[
                    self.metadata[key][TVTOSSN]
                ][1](value)
        else:
            raise KeyError


__all__ = ["Record",]
