"""Metadata object"""
from csv import DictReader, DictWriter
from html.parser import HTMLParser
from itertools import groupby
from logging import getLogger
from re import compile, finditer, sub

from .util import record_type_map

LOGGER = getLogger(__name__)


class SQL:
    create_schema = "CREATE SCHEMA IF NOT EXISTS {};\n"
    create_table = "CREATE TABLE IF NOT EXISTS {}();\n"
    add_column = "ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {};\n"


COLUMNS = [
    "field_name", "form_name", "section_header", "field_type", "field_label",
    "select_choices_or_calculations", "field_note",
    "text_validation_type_or_show_slider_number" ,"text_validation_min",
    "text_validation_max", "identifier", "branching_logic", "required_field",
    "custom_alignment", "question_number", "matrix_group_name", "matrix_ranking",
    "field_annotation"
]


LOAD_VARIABLE_RE = compile(r"\[[\w()]+\]")
LOAD_OPERATOR_RE = compile(r"<>|\s=\s|\w=\w")
DUMP_VARIABLE_RE = compile(r"record\['[\w]+'\]")
DUMP_OPERATOR_RE = compile(r"==|!=")


class Metadata(dict):
    """REDCap metadata abstraction"""

    def __init__(self, raw_metadata=None, raw_field_names=None):
        """Contructor"""
        if raw_metadata is not None and raw_field_names is not None:
            self.raw_metadata = {d["field_name"]: d for d in raw_metadata}
            self.raw_field_names = {
                d["export_field_name"]: d for d in raw_field_names
            }
        super().__init__()

    def __getitem__(self, key):
        """Lazy getter"""
        if key not in self:
            raw_metadatum = self.raw_metadata.pop(
                self.raw_field_names[key]["original_field_name"]
            )
            raw_metadatum["branching_logic"] = self.load_logic(
                raw_metadatum["branching_logic"]
            )
            self.__setitem__(key, raw_metadatum)
        return super().__getitem__(key)
        
    def evaluate_logic(self, record):
        """Return truthness of record's branching logic"""
        if not record: return None
        try: logic = eval(logic)
        except SyntaxError: logic = eval(self.load_logic(logic))
        else: return logic

    def load_logic(self, logic):
        """Convert REDCap logic syntax to Python logic syntax"""
        if not logic: return ""
        for match in LOAD_VARIABLE_RE.finditer(logic):
            var_str = match.group(0).strip("[]")
            if "(" in var_str and ")" in var_str:
                var_str = "___".join(s.strip(")") for s in var_str.split("("))
            var_str = "record['" + var_str + "']"
            logic = logic[:match.start()] + var_str + logic[:match.end()]
        for match in LOAD_OPERATOR_RE.finditer(logic):
            ope_str = match.group(0)
            if ope_str == "=": ope_str = "=="
            elif ope_str == "<>": ope_str = "!="
            logic = logic[:match.start()] + ope_str + logic[:match.end()]
        return logic

    def dump_logic(self, logic):
        """Convert Python logic syntax to REDCap logic syntax"""
        if not logic:
            return ""
        for match in DUMP_VARIABLE_RE.finditer(logic):
            var_str = match.group(0).lstrip("record['").rstrip("']")
            if "___" in var_str:
                var_str = "(".join(var_str.split("___")) + ")"
            var_str = "[" + var_str + "]"
            logic = logic[:match.start()] + var_str + logic[:match.end()]
        for match in DUMP_OPERATOR_RE.finditer(logic):
            ope_str = match.group(0)
            if ope_str == "==": ope_str = "="
            elif ope_str == "!=": ope_str = "<>"
            logic = logic[:match.start()] + ope_str + logic[:match.end()]
        return logic

    def dump(self, path, fmt="csv", **kwargs):
        """Dump formatted metadata to path"""
        for field_name in self:
            self[field_name]["branching_logic"] = self.dump_logic(
                self[field_name]["branching_logic"]
            )
        if fmt == "csv":
            with open(path, "w", newline="") as fp:
                writer = DictWriter(fp, fieldnames=COLUMNS)
                writer.writeheader()
                for metadatum in self.raw_metadata:
                    writer.writerow(metadatum)
                for metadatum in self.values():
                    writer.writerow(metadatum)
        elif fmt == "sql_migration":
            with open(path, "w", newline="") as fp:
                if "schema" in kwargs:
                    fp.write(SQL.create_schema.format(kwargs["schema"]))
                    schema = kwargs["schema"] + "."
                else:
                    schema = ""
                if "table_groups" in kwargs:
                    if kwargs["table_groups"] not in COLUMNS:
                        raise Exception("Invalid table grouping :/")
                    table_groups = kwargs["table_groups"]
                else:
                    table_groups = "field_type"
                key = lambda d: d[table_groups]
                for table, columns in groupby(
                    sorted(list(self.values()) + self.raw_metadata, key=key),
                    key=key
                ):
                    fp.write(SQL.create_table.format(schema + table))
                    for c in columns:
                        fp.write(
                            SQL.add_column.format(
                                schema + table,
                                c["field_name"],
                                record_type_map[
                                    c["text_validation_type_or_show_slider_number"]
                                ][2]
                            )
                        )
        elif fmt == "html_table":
            pass
        for field_name in self:
            self[field_name]["branching_logic"] = self.load_logic(
                self[field_name]["branching_logic"]
            )

    def load(self, raw_metadata, raw_field_names):
        """Load metadata from raw metadata and raw field names"""
        self.raw_metadata = raw_metadata
        self.raw_field_names = raw_field_names
        if len(self) > 0:
            for key in list(self.keys()):
                del self[key]


__all__ = ["Metadata"]
