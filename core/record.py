"""Record casting tools"""

from .util import record_type_map


def load_record(record, metadata):
    """Return record with Python typing"""
    for k,v in record.items():
        record[k] = record_type_map[
            metadata[k]["text_validation_type_or_show_slider_number"]
        ][0](v)


def dump_record(record, metadata):
    """Return Pythonic record as JSON-compliant dict"""
    for k,v in record.items():
        record[k] = record_type_map[
            metadata[k]["text_validation_type_or_show_slider_number"]
        ][1](v)
