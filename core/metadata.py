"""Metadata object"""
from csv import DictReader, DictWriter
from html.parser import HTMLParser
from itertools import groupby
from logging import getLogger
from re import compile, finditer, sub

from .util import record_type_map


LOGGER = getLogger(__name__)


HTML = """
  <!DOCTYPE html>
  <html lang="en">
  <head>
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >
  </head>
  <body><table style="width:100%">{}</table></body>
  </html>
""".strip()


class HTMLParser(HTMLParser):
    pass


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


class Metadata:
    """REDCap metadata abstraction"""

    def __getitem__(self, key):
        """Get metadatum"""
        metadatum = self.raw_metadata[
            self.raw_field_names[key]["original_field_name"]
        ]
        metadatum["branching_logic"] = self.load_logic(
            metadatum["branching_logic"], as_func=True
        )
        return metadatum

    def __init__(self, raw_metadata={}, raw_field_names={}):
        """Contructor"""
        self.raw_metadata = {d["field_name"]: d for d in raw_metadata}
        self.raw_field_names = {
            d["export_field_name"]: d for d in raw_field_names
        }

    def __iter__(self):
        """Return raw metadata iterator"""
        return self.raw_metadata

    def __len__(self):
        """Return field count"""
        return len(self.raw_metadata)

    @classmethod
    def load_logic(cls, logic, as_func=False):
        """Return evaluable branching logic"""
        if not logic:
            return ""
        for match in LOAD_VARIABLE_RE.finditer(logic):
            var_str = match.group(0).strip("[]")
            if "(" in var_str and ")" in var_str:
                var_str = "___".join(
                    s.strip(")") for s in var_str.split("(")
                )
            var_str = "record['" + var_str + "']"
            logic = logic[:match.start()] + var_str + logic[:match.end()]
        for match in LOAD_OPERATOR_RE.finditer(logic):
            ope_str = match.group(0)
            if ope_str == "=":
                ope_str = "=="
            elif ope_str == "<>":
                ope_str = "!="
            logic = logic[:match.start()] + ope_str + logic[:match.end()]
        if as_func:
            return lambda record: eval(logic)
        return logic

    @classmethod
    def dump_logic(cls, logic):
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

    def load_record(self, record):
        """Return record with Python typing"""
        for k,v in record.items():
            k = self.raw_field_names[k]["original_field_name"]
            record[k] = record_type_map[
                self[k]["text_validation_type_or_show_slider_number"]
            ][0](v)
        return record

    def dump_record(self, record):
        """Return Pythonic record as JSON-compliant dict"""
        for k,v in record.items():
            k = self.raw_field_names[k]["original_field_name"]
            record[k] = record_type_map[
                self[k]["text_validation_type_or_show_slider_number"]
            ][1](v)
        return record

    def dump(self, path, fmt="csv"):
        """Dump formatted metadata to path"""
        if len(self) == 0:
            raise Exception("Cannot dump empty metadata")
        if fmt == "csv":
            with open(path, "w", newline="") as fp:
                writer = DictWriter(fp, fieldnames=COLUMNS)
                writer.writeheader()
                for metadatum in self.raw_metadata:
                    writer.writerow(metadatum)
        elif fmt == "html":
            td = '<td><input type="text" value="{}"></td>'
            with open(path, "w") as fp:
                html = (
                    '<tr>' +
                    "".join('<td>{}</td>'.format(c) for c in COLUMNS)
                    + '</tr>'
                )
                for metadatum in self.raw_metadata.values():
                    row = ""
                    for c in COLUMNS:
                        row += td.format(metadatum[c])
                    html += '<tr>' + row + '</tr>'
                fp.write(HTML.format(html))
        else:
            raise Exception("unsupported dump format")

    def load(self):
        """WIP"""
        pass
        
    def sql_migration(self, path, schema="", table_groups="field_type"):
        """Write a SQL migration file from metadata"""
        if schema: schema += "."
        with open(path, "w") as fp:
            fp.write(SQL.create_schema.format(schema))
            if table_groups not in COLUMNS:
                raise Exception("Invalid table grouping :/")
            for table, columns in groupby(
                sorted(
                    list(self.values()) + self.raw_metadata,
                    key=lambda d: d[table_groups]
                ),
                key=lambda d: d[table_groups]
            ):
                fp.write(SQL.create_table.format(schema + table))
                for c in columns:
                    fp.write(
                        SQL.add_column.format(
                            schema + table,
                            c["field_name"],
                            record_type_map[c[COLUMNS[7]]][2]
                        )
                    )

__all__ = ["Metadata",]
