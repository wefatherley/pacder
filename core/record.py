"""Record object"""

from .util import record_type_map


class Record(dict):
    def load(self, metadata):
        """Return record with Python typing"""
        for k,v in self.items():
            self[k] = record_type_map[
                metadata[k]["text_validation_type_or_show_slider_number"]
            ][0](v)

    def dump(self, metadata):
        """Return Pythonic record as JSON-compliant dict"""
        for k,v in self.items():
            self[k] = record_type_map[
                metadata[k]["text_validation_type_or_show_slider_number"]
            ][1](v)


def record_factory(): pass