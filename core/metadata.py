"""Metadata and associated objects"""
from csv import DictReader, DictWriter
from html.parser import HTMLParser
from itertools import groupby, zip_longest
from json import dump as dump_json, load as load_json
from logging import getLogger
from re import compile, finditer, sub

from .util import record_type_map


LOGGER = getLogger(__name__)


COLUMNS = [
    "field_name", "form_name", "section_header", "field_type",
    "field_label", "select_choices_or_calculations", "field_note",
    "text_validation_type_or_show_slider_number" ,"text_validation_min",
    "text_validation_max", "identifier", "branching_logic",
    "required_field", "custom_alignment", "question_number",
    "matrix_group_name", "matrix_ranking", "field_annotation",
]


class HTMLParser(HTMLParser):
    """Extract metadata from HTML string"""

    raw_metadata = dict()

    def feed(self, data):
        """Feed in raw metadata HTML string"""
        if self.raw_metadata:
            self.raw_metadata = dict()
        super().feed(data)
        self.raw_metadata = [v for v in self.raw_metadata.values()]
        return self.raw_metadata

    def handle_startendtag(self, tag, attrs):
        """Extract metadata elements"""
        if tag == "td":
            column_name, index = attrs["for"].split("_")
            try:
                self.raw_metadata[index][column_name] = attrs["value"]
            except KeyError:
                self.raw_metadata[index] = {column_name: attrs["value"]}


HTML_TABLE_RE = compile(r"(/\*pacder\*/)")


class SQL:
    create_schema = "CREATE SCHEMA IF NOT EXISTS {};\n"
    create_table = "CREATE TABLE IF NOT EXISTS {}();\n"
    add_column = "ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {};\n"


LOAD_VARIABLE_RE = compile(r"\[[\w()]+\]")
LOAD_OPERATOR_RE = compile(r"(?<![<\|>]{1})=|<>")
DUMP_VARIABLE_RE = compile(r"record\['\w+'\]")
DUMP_OPERATOR_RE = compile(r"==|!=")


class Metadata:
    """Container for REDCap metadata"""
    
    html_parser = HTMLParser()

    def __getitem__(self, key):
        """Get metadatum"""
        if len(self.raw_field_names) == 0:
            raise Exception("No export field names")
        metadatum = self.raw_metadata[
            self.raw_field_names[key]["original_field_name"]
        ]
        metadatum["branching_logic"] = self.load_logic(
            metadatum["branching_logic"], as_func=True
        )
        return metadatum

    def __init__(self, raw_metadata={}, raw_field_names={}):
        """Contruct attributes"""
        self.raw_metadata = {d["field_name"]: d for d in raw_metadata}
        self.raw_field_names = {
            d["export_field_name"]: d for d in raw_field_names
        }

    def __iter__(self):
        """Return raw metadata iterator"""
        return (m for m in self.raw_metadata)

    def __len__(self):
        """Return field count"""
        return len(self.raw_metadata)

    def __setitem__(self, key, value):
        """Set metadatum"""
        if value["field_type"] == "checkbox":
            self.raw_metadata[key] = value
            for exported_key in [
                field_name.split(",")[-1].strip()
                for field_name in value[
                    "select_choices_or_calculations"
                ].split("|")
            ]:
                self.raw_field_names[exported_key] = {
                    "original_field_name": key,
                    "export_field_name": exported_key
                }
        else:
            self.raw_metadata[key] = value
            self.raw_field_names[key] = {
                "original_field_name": key,
                "export_field_name": key
            }

    @classmethod
    def load_logic(cls, logic, as_func=False):
        """Return evaluable branching logic"""
        if not logic:
            if as_func: return lambda record: None
            return ""
        logic_fragments = zip_longest(
            LOAD_VARIABLE_RE.split(logic),
            [m.group(0) for m in LOAD_VARIABLE_RE.finditer(logic)],
            fillvalue=""
        )
        logic = ""
        for oper_frag, vari_frag in logic_fragments:
            for match in LOAD_OPERATOR_RE.finditer(oper_frag):
                ope_str = match.group(0)
                if ope_str == "=": ope_str = "=="
                elif ope_str == "<>": ope_str = "!="
                oper_frag = (
                    oper_frag[:match.start()]
                    + ope_str
                    + oper_frag[match.end():]
                )
            if vari_frag:
                vari_frag = vari_frag.strip("[]")
                if "(" in vari_frag and ")" in vari_frag:
                    vari_frag = "___".join(
                        s.strip(")") for s in vari_frag.split("(")
                    )
                vari_frag = "record['" + vari_frag + "']"
            logic += oper_frag + vari_frag
        if as_func:
            return lambda record: eval(logic)
        return logic

    @classmethod
    def dump_logic(cls, logic):
        """Convert Python logic syntax to REDCap logic syntax"""
        if not logic:
            return ""
        logic_fragments = zip_longest(
            DUMP_VARIABLE_RE.split(logic),
            [m.group(0) for m in DUMP_VARIABLE_RE.finditer(logic)],
            fillvalue=""
        )
        logic = ""
        for oper_frag, vari_frag in logic_fragments:
            for match in DUMP_OPERATOR_RE.finditer(oper_frag):
                ope_str = match.group(0)
                if ope_str == "==": ope_str = "="
                elif ope_str == "!=": ope_str = "<>"
                oper_frag = (
                    oper_frag[:match.start()]
                    + ope_str
                    + oper_frag[match.end():]
                )
            if vari_frag:
                vari_frag = vari_frag.lstrip("record['").rstrip("']")
                if "___" in vari_frag:
                    vari_frag = "(".join(
                        s for s in vari_frag.split("___")
                    ) + ")"
                vari_frag = "[" + vari_frag + "]"
            logic += oper_frag + vari_frag
        return logic

    def load_record(self, record):
        """Return record with Python typing"""
        if len(self.raw_field_names) == 0:
            raise Exception("No field name mapping!!")
        for k,v in record.items():
            ofn = self.raw_field_names[k]["original_field_name"]
            v = record_type_map[
                self[ofn]["text_validation_type_or_show_slider_number"]
            ][0](v)
            logic = self.load_logic(
                self.raw_metadata[ofn]["branching_logic"], as_func=True
            )(v)
            record[k] = Datum(k, v, logic)
        return record

    def dump_record(self, record):
        """Return Pythonic record as JSON-compliant dict"""
        if len(self.raw_field_names) == 0:
            raise Exception("No field name mapping!!")
        for k,v in record.items():
            k = self.raw_field_names[k]["original_field_name"]
            record[k] = record_type_map[
                self[k]["text_validation_type_or_show_slider_number"]
            ][1](v.value)
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
        elif fmt == "json":
            with open(path, "w") as fp:
                dump_json(self.raw_metadata, fp)
        elif fmt == "html":
            td = '<td><input type="text" for="{}" value="{}"></td>'
            table = (
                '<tr><td></td>'
                + "".join('<td>{}</td>'.format(c) for c in COLUMNS)
                + '</tr>'
            )
            for i in range(len(self.raw_metadata)):
                row = ""
                for c in COLUMNS:
                    metadatum = self.raw_metadata[i][c]
                    c += "_{}".format(str(i))
                    row += td.format(c, metadatum)
                table += (
                    '<tr><td><input type="checkbox"></td>'
                    + row
                    + '</tr>'
                )
            with open(path, "w") as fp:
                fp.write(HTML_TABLE_RE.sub(html))
        else:
            raise Exception("unsupported dump format")

    def load(self, path, fmt="csv"):
        """Load formatted metadata from path"""
        if isinstance(path, str):
            if fmt == "csv":
                path = open(path, "r", newline="")
            else: 
                path = open(path, "r")
        if fmt == "csv":
            with path:
                reader = DictReader(path, fieldnames=COLUMNS)
                for row in reader:
                    self[row["field_name"]] = row
        elif fmt == "json":
            with path:
                metadata = load_json(path)
            while any(metadata):
                metadatum = metadata.pop()
                self[metadatum["field_name"]] = metadatum
        elif fmt == "html":
            self.raw_metadata = self.html_parser.feed(path.read())
        else:
            raise Exception("unsupported load format")
        path.close()

    def sql_migration(self, path, schema="", table_groups="field_type"):
        """Write a SQL migration file from metadata"""
        if schema: schema += "."
        with open(path, "w") as fp:
            fp.write(SQL.create_schema.format(schema))
            if table_groups not in COLUMNS:
                raise Exception("Invalid table grouping :/")
            for table, columns in groupby(
                sorted(self.raw_metadata, key=lambda d: d[table_groups]),
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
