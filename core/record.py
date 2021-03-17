"""Record objects"""
from logging import getLogger

from .util import data_type_map


LOGGER = getLogger(__name__)


class Record:
    """Record object"""

    def __delitem__(sellf, key):
        """Delete record datum"""
        pass

    def __getitem__(self, key, value):
        """Get record datum"""
        pass
    
    def __init__(self, raw_record, metadata):
        """Record constructor"""
        self.metadata = metadata
        self.raw_record = raw_record

    def __len__(self):
        return len(self.raw_record)

    def __setitem__(self, key, value):
        """Set record datum"""
        pass




    # def load_record(self, record):
    #     """Return record with Python typing"""
    #     if len(self.raw_field_names) == 0:
    #         raise Exception("No field name mapping!!")
    #     for k,v in record.items():
    #         ofn = self.raw_field_names[k]["original_field_name"]
    #         v = record_type_map[
    #             self[ofn]["text_validation_type_or_show_slider_number"]
    #         ][0](v)
    #         logic = self.load_logic(
    #             self.raw_metadata[ofn]["branching_logic"], as_func=True
    #         )(v)
    #         record[k] = Datum(k, v, logic)
    #     return record

    # def dump_record(self, record):
    #     """Return Pythonic record as JSON-compliant dict"""
    #     if len(self.raw_field_names) == 0:
    #         raise Exception("No field name mapping!!")
    #     for k,v in record.items():
    #         k = self.raw_field_names[k]["original_field_name"]
    #         record[k] = record_type_map[
    #             self[k]["text_validation_type_or_show_slider_number"]
    #         ][1](v.value)
    #     return record


__all__ = ["Record",]
