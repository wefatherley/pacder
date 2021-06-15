"""Metadata and associated objects"""
from csv import DictReader, DictWriter
from html.parser import HTMLParser
from io import IOBase
from itertools import groupby, zip_longest
from json import (
    dump as json_dump,
    dumps as json_dumps,
    load as json_load, 
    loads as json_loads
)
from logging import getLogger
from re import compile, finditer, sub

from .util import data_type_map


__all__ = ["Metadata",]


LOGGER = getLogger(__name__)


COLUMNS = [
    "field_name", "form_name", "section_header", "field_type",
    "field_label", "select_choices_or_calculations", "field_note",
    "text_validation_type_or_show_slider_number",
    "text_validation_min", "text_validation_max", "identifier",
    "branching_logic", "required_field", "custom_alignment",
    "question_number", "matrix_group_name", "matrix_ranking",
    "field_annotation",
]


LOAD_VARIABLE_RE = compile(r"\[[\w()]+\]")
LOAD_OPERATOR_RE = compile(r"(?<![<\|>]{1})=|<>")
DUMP_VARIABLE_RE = compile(r"record\['\w+'\]")
DUMP_OPERATOR_RE = compile(r"==|!=")


def dump_field_name(value):
    """dump field_name"""
    return value


def load_field_name(value):
    """load field_name"""
    return value


def dump_form_name(value):
    """dump form_name"""
    return value


def load_form_name(value):
    """load form_name"""
    return value


def dump_section_header(value):
    """dump section_header"""
    return value


def load_section_header(value):
    """load section_header"""
    return value


def dump_field_type(value):
    """dump field_type"""
    return value


def load_field_type(value):
    """load field_type"""
    return value


def dump_field_label(value):
    """dump field_label"""
    return value


def load_field_label(value):
    """load field_label"""
    return value


def dump_select_choices_or_calculations(value):
    """dump select_choices_or_calculations"""
    return value


def load_select_choices_or_calculations(value):
    """load select_choices_or_calculations"""
    return value


def dump_field_note(value):
    """dump field_note"""
    return value


def load_field_note(value):
    """load field_note"""
    return value


def dump_text_validation_type_or_show_slider_number(value):
    """dump text_validation_type_or_show_slider_number"""
    return value


def load_text_validation_type_or_show_slider_number(value):
    """load text_validation_type_or_show_slider_number"""
    return value


def dump_text_validation_min(value):
    """dump text_validation_min"""
    return value


def load_text_validation_min(value):
    """load text_validation_min"""
    return value


def dump_text_validation_max(value):
    """dump text_validation_max"""
    return value


def load_text_validation_max(value):
    """load text_validation_max"""
    return value


def dump_identifier(value):
    """dump identifier"""
    if value is True:
        return "y"
    return "n"


def load_identifier(value):
    """load identifier"""
    if value == "y":
        return True
    return False


def dump_branching_logic(value):
    """dump branching_logic"""
    if not value:
        return ""
    logic_fragments = zip_longest(
        DUMP_VARIABLE_RE.split(value),
        [m.group(0) for m in DUMP_VARIABLE_RE.finditer(value)],
        fillvalue=""
    )
    value = ""
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
        value += oper_frag + vari_frag
    return value


def load_branching_logic(value):
    """load branching_logic"""
    if not value:
        return ""
    logic_fragments = zip_longest(
        LOAD_VARIABLE_RE.split(value),
        [m.group(0) for m in LOAD_VARIABLE_RE.finditer(value)],
        fillvalue=""
    )
    value = ""
    for oper_frag, vari_frag in logic_fragments:
        for match in LOAD_OPERATOR_RE.finditer(oper_frag):
            ope_str = match.group(0)
            if ope_str == "=":
                ope_str = "=="
            elif ope_str == "<>":
                ope_str = "!="
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
        value += oper_frag + vari_frag
    return value


def dump_required_field(value):
    """dump required_field"""
    if value is True:
        return "y"
    return "n"


def load_required_field(value):
    """load required_field"""
    if value == "y":
        return True
    return False


def dump_custom_alignment(value):
    """dump custom_alignment"""
    return value


def load_custom_alignment(value):
    """load custom_alignment"""
    return value


def dump_question_number(value):
    """dump question_number"""
    return value


def load_question_number(value):
    """load question_number"""
    return value


def dump_matrix_group_name(value):
    """dump matrix_group_name"""
    return value


def load_matrix_group_name(value):
    """load matrix_group_name"""
    return value


def dump_matrix_ranking(value):
    """dump matrix_ranking"""
    return value


def load_matrix_ranking(value):
    """load matrix_ranking"""
    return value


def dump_field_annotation(value):
    """dump field_annotation"""
    return value


def load_field_annotation(value):
    """load field_annotation"""
    return value


def dump_metadatum(value):
    """load metadatum"""
    for column in COLUMNS:
        func = eval("dump_{}".format(column))
        value[column] = func(value[column])
    return value


def load_metadatum(value):
    """load metadatum"""
    if sorted(value.keys()) != sorted(COLUMNS):
        raise Exception("invalid metadatum")
    for column in COLUMNS:
        func = eval("load_{}".format(column))
        value[column] = func(value[column])
    return value


TemplateHTML = """
    <!DOCTYPE html>
    <html>
        <head>
        </head>
        <body>
        <table id="metadata">{}</table>
        </body>
    </html>
""".strip()


class HTMLParser(HTMLParser):
    """extract metadata from HTML string"""
    pass


class TemplateSQL:
    """statements for rendering SQL migration"""
    create_schema = "CREATE SCHEMA IF NOT EXISTS {};\n"
    create_table = "CREATE TABLE IF NOT EXISTS {}();\n"
    add_column = "ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {};\n"


class Metadata(dict):
    """container for REDCap metadata"""

    def __contains__(self, field):
        """implement `in` operator"""
        if field in self.field_map:
            return True
        return False

    def __getitem__(self, field):
        """get metadatum"""
        return super().__getitem__(
            self.field_map[field]["original_field_name"]
        )

    def __init__(self, raw_metadata=dict(), **kwargs):
        """construct instance"""
        self.project = kwargs.get("project")
        if self.project and not raw_metadata:
            with self.project.connector as conn:
                raw_metadata = json_loads(conn.metadata("export"))
                field_map = json_loads(conn.field_names("export"))
        super().__init__()
        for metadatum in raw_metadata:
            self[metadatum[COLUMNS[0]]] = load_metadatum(metadatum)
        self.field_map = {
            field["export_field_name"]: field for field in field_map
        }

    def __setitem__(self, field, value):
        """set metadatum"""
        if field not in value:
            value[COLUMNS[0]] = field
        super().__setitem__(field, value)

    def csv(self):
        """return CSV string"""
        csv = ", ".join(COLUMNS) + "\n"
        for row in self.raw():
            csv += ", ".join(row.values()) + "\n"
        return csv

    def html(self, writable=False):
        """return HTML string"""
        pass

    def json(self):
        """return JSON string"""
        return json_dumps(self.raw())

    def raw(self, key=COLUMNS[1]):
        """return non-type-casted list of dictionaries"""
        return sorted(
            (dump_metadatum(md) for md in self.values()),
            key=lambda d: d[key]
        )

    def sql(self, schema="", table_groups=COLUMNS[3]):
        """return SQL migration string"""
        sql = ""
        if schema:
            schema += "."
            sql += TemplateSQL.create_schema.format(schema)
        if table_groups not in COLUMNS:
            raise Exception("invalid table grouping")
        for table, columns in groupby(
            sorted(self.raw(), key=lambda d: d[table_groups]),
            key=lambda d: d[table_groups]
        ):
            sql += TemplateSQL.create_table.format(schema + table)
            for c in columns:
                sql += TemplateSQL.add_column.format(
                    schema + table,
                    c["field_name"],
                    data_type_map[c[COLUMNS[7]]][2]
                )
        return sql
