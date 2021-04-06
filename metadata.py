"""Metadata and associated objects"""
from csv import DictReader, DictWriter
from html.parser import HTMLParser
from io import TextIOBase
from itertools import groupby, zip_longest
from json import (
    dump as dump_json, load as load_json, loads as loads_json
)
from logging import getLogger
from re import compile, finditer, sub

from .util import data_type_map


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
            col_name, index = attrs["for"].split("_")
            try:
                self.raw_metadata[index][col_name] = attrs["value"]
            except KeyError:
                self.raw_metadata[index] = {col_name: attrs["value"]}


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
    
    columns = COLUMNS
    html_parser = HTMLParser()

    def __contains__(self, item):
        """Implement membership test operators"""
        if "___" in item and item in self.raw_field_names:
            return True
        if item in self.raw_metadata:
            return True
        return False

    def __delitem__(self, key):
        """Delete metadatum"""
        if "___" in key:
            raise Exception("can't delete a single checkbox field")
        if key not in self.raw_metadata:
            raise KeyError
        if self.raw_metadata[key]["field_type"] == "checkbox":
            for c in value[
                "select_choices_or_calculations"
            ].split("|"):
                del self.raw_field_names[
                    key + "___" + c.split(",")[0].strip()
                ]
        del self.raw_metadata[key]

    def __eq__(self, other):
        """Implement `==`"""
        if type(self) is not type(other):
            return NotImplemented
        if (
            hasattr(other, "items")
            and hasattr(other, "raw_field_names")
            and hasattr(other, "raw_metadata")
        ):
            if (
                other.items == self.items
                and other.raw_field_names == self.raw_field_names
                and other.raw_metadata == self.raw_metadata
            ):
                return True
        return False
        

    def __getitem__(self, key):
        """Get lazily-casted metadatum"""
        try:
            return self.items[key]
        except KeyError:
            if "___" in key:
                if key not in self.raw_field_names:
                    raise KeyError
                md = self.raw_metadata[
                    self.raw_field_names[key]["original_field_name"]
                ]
            elif key in self.raw_metadata:
                md = self.raw_metadata[key]
            else:
                raise KeyError
            if md["field_type"] in {"checkbox", "radio"}:
                md["select_choices_or_calculations"] = {
                    int(k.strip()): v.strip()
                    for k,v in (
                        md[
                            "select_choices_or_calculations"
                        ].split("|")
                    ).split(",")
                }
            md["branching_logic"] = self.load_logic(
                md["branching_logic"], as_func=True
            )
            md["required_field"] = False
            if md["required_field"] == "y":
                md["required_field"] = True
            md["identifier"] = False
            if md["identifier"] == "y":
                md["identifier"] = True
            self.items[key] = md
            return md

    def __init__(self, raw_metadata, raw_field_names, **kwargs):
        """Contruct attributes"""
        self.items = dict()
        self.raw_metadata = {
            d["field_name"]: d for d in raw_metadata
        }
        self.raw_field_names = {
            d["export_field_name"]: d for d in raw_field_names
        }
        if "project" in kwargs:
            self.project = kwargs["project"]

    def __iter__(self):
        """Return raw metadata iterator"""
        return (
            self.__getitem__(key) for key in self.raw_field_names
        )

    def __len__(self):
        """Return field count"""
        return len(self.raw_metadata)

    def __setitem__(self, key, value):
        """Set metadata field"""
        if "field_name" not in value:
            value["field_name"] = key
        if list(value.keys()) != self.columns:
            raise Exception("New field missing columns")
        self.raw_metadata.append(value)
        ofn = value["field_name"]
        if value["field_type"] == "checkbox":
            for c in value[
                "select_choices_or_calculations"
            ].split("|"):
                efn = ofn + "___" + c.split(",")[0].strip()
                self.raw_field_names.append(
                    {
                        "original_field_name": ofn,
                        "export_field_name": efn,
                    }
                )
        else:
            self.raw_field_names.append(
                {
                    "original_field_name": ofn,
                    "export_field_name": ofn,
                }
            )
        LOGGER.info(
            "added to metadata: field_name=%s, field_type=%s",
            value["field_name"],
            value["field_type"]
        )

    @classmethod
    def load_calculation(cls, calculation, as_func=False):
        """Return evaluable field calculation"""
        raise NotImplementedError

    @classmethod
    def dump_calculation(cls, calculation):
        """Return evaluable field calculation"""
        raise NotImplementedError

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

    def dump(self, fp, fmt="csv", close_fp=True):
        """Dump formatted metadata to file pointer"""
        if len(self) == 0:
            raise Exception("Cannot dump empty metadata")
        if isinstance(fp, str):
            if fmt == "csv": fp = open(fp, "w", newline="")
            else: fp = open(fp, "w")
        if fmt == "csv":
            writer = DictWriter(fp, fieldnames=COLUMNS)
            writer.writeheader()
            for metadatum in self.raw_metadata:
                writer.writerow(metadatum)
        elif fmt == "json":
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
            fp.write(HTML_TABLE_RE.sub(html))
        else:
            raise Exception("unsupported dump format")
        if not close_fp: return fp
        fp.close()

    def load(self, fp, fmt="csv"):
        """Load formatted metadata from file pointer"""
        if isinstance(fp, str):
            if fmt == "csv": fp = open(fp, "r", newline="")
            else: fp = open(fp, "r")
        if fmt == "csv":
            with fp:
                reader = DictReader(fp, fieldnames=COLUMNS)
                for row in reader:
                    self[row["field_name"]] = row
        elif fmt == "json":
            with fp:
                metadata = load_json(fp)
            while any(metadata):
                metadatum = metadata.pop()
                self[metadatum["field_name"]] = metadatum
        elif fmt == "html":
            with fp:
                self.raw_metadata = self.html_parser.feed(fp.read())
        else:
            raise Exception("unsupported load format")

    def push(self):
        """Alias for `Project.connector.metadata("import", ...)`"""
        if hasattr(self, "project"):
            try:
                LOGGER.info("pushing project metadata")
                resp = self.project.connector.metadata(
                    "import", self.dump(TextIOBase(), close_fp=False)
                )
            except Exception as e:
                LOGGER.exception("push raised exception: exc=%s", e)
                raise
            else:
                LOGGER.info("pushed project metadata")
        else:
            raise Exception("Cannot push metadata changes")

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
                            data_type_map[c[COLUMNS[7]]][2]
                        )
                    )


__all__ = ["Metadata",]
