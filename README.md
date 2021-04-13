# WIP pacder

[![Documentation Status](https://readthedocs.org/projects/pacder/badge/?version=latest)](https://pacder.readthedocs.io/en/latest/?badge=latest)

Exposes REDCap's API through the Python programming langauge, allowing token holders to __delete__, __export__, and __import__ project content. Use this package to develop ETL flows, project analyses, interview clients, and so on.

CONTRIBUTING: Please contribute, this package is still in it's infancy.

## Install
Built on top of the Python standard library, and available for __Python 3.6+__. Install the latest stable release with `pip`:

`python3 -m pip install pacder`,

or with `conda`:

`conda install -c pacder`.

## Usage
### Programmatic usage
At the lowest level, `pacder` exposes a REDCap project with it's `Connector` object:

```python
# First, find your API location/credentials, e.g.,
from os import getenv

host = getenv["REDCAP_HOST"] # e.g. redcap.myorg.net
path = getenv["REDCAP_PATH"] # e.g. /apps/redcap/api/
token = getenv["REDCAP_PROJECT123_TOKEN"] # e.g. sf11gk2herg3o34d...


# import the connector object
from pacder import Connector


# use connector object as a context manager (or not)
with Connector(host, path, token) as conn:

    # remove a file from the project
    conn.delete_content("files", name="virus.png")
    # or, identically,
    conn.files("delete", name="virus.png")

    # fetch some records
    records_bytes = conn.export_content("records", format="csv", filterLogic="[age] > 30", ...)
    # or, identically,
    records_bytes = conn.records("export", format="csv", filterLogic="[age] > 30", ...)

    # update a project's metadata
    with open("project_metadata.csv", "r") as fp:
        conn.import_content("metadata", fp)
        # or, identically,
        conn.metadata("import", fp)
```

In addition to a basic client, `pacder` also provides a `Project` object that makes dealing with REDCap abstractions in Python simple:

```python
from datetime import date

from pacder import Project

# use project object as a context manager (or not)
with Project(host, path, token) as proj:

    # handle and inspect records
    for record in proj.records(filterLogic="[age] < 65"):

        # perform logical comparisons with Python typing
        if (
            record["sign_up_date"].value < date(2021, 5, 1)
            and not record["comorbitiy_count"].valid
        ):
            print("{} signed up too early!!".format(record["name"].value))

    # alter project by adding a new field
    proj.metadata["vaccine_manufacturer"] = {"field_type": "radio", ...}
    # hide a replaced field
    proj.metadata["vaccine"]["field_annotation"] = "@HIDDEN"
    # push metadata changes to the REDCap instance
    proj.metadata.push()

    # create a SQL migration from project metadata for auxiliary relational datastore
    proj.sql_migration("/migrations/myproject.sql")
    # by default the migration has tables that go by field type,
    # but they can be made to go by, e.g., form name
    proj.sql_migration("/migrations/myproject.sql", table_groups="form_name")
```

## Documentation
Available on [readthedocs](https://pacder.readthedocs.io).
