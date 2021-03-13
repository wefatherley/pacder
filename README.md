# WIP pacder
This package furnishes programmatic access to a REDCap instance's API, allowing token holders to __delete__, __export__, and __import__ content related to one or more of their projects.

## Install
Available for __Python 3.6+__. There are no dependencies other than the Python standard library. 

Install the latest stable release with `pip`:

`python3 -m pip install pacder`,

or with `conda`:

`conda install -c pacder`.

## Usage
At the lowest level, `pacder` exposes a REDCap project with a `Connector` object:

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
    conn.delete_content("files", name="flowers.png")
    # or, identically,
    conn.files("delete", name="flowers.png")

    # fetch some records (a list of dicts)
    my_records = conn.export_content("records", format="csv", filterLogic="[age] > 30")
    # or, identically,
    my_records = conn.records("export", format="csv", filterLogic="[age] > 30")

    # update a project's metadata
    with open("project_metadata.csv", "r") as fp:
        conn.import_content("metadata", fp)
        # or, identically,
        conn.metadata("import", fp)
```

In addition to acting as a low-level client, `pacder` also provides a `Project` object that performs type casting, and other useful features:

```python
from datetime import date

from pacder import Project

# use project object as a context manager (or not)
with Project(host, path, token) as pj:

    # handle and inspect records
    for record in pj.records(filterLogic="[age] > 65"):

        # get the original field name of a checkbox variable
        comorbids_ofn = record["comorbid___123"].original_field_name

        # perform temporal comparisons
        if record["sign_up_date"].value < date(2021, 5, 1):
            print("{} signed up too early!!".format(record["name"].value))

        # verify interview went as supposed
        if record["available_vax_sites"].logic:
            print("{} saw vax sites!!".format(record["name"].value))

    # alter project metadata
    pj.update_metadata({"field_name": "vaccine_type", ...})

    # create a SQL migration from project metadata for auxiliary relational datastore
    pj.sql_migration("/migrations/myproject.sql")
    # by default the migration has tables that represent field type,
    # but one can go by, e.g., form name
    pj.sql_migration("/migrations/myproject.sql", table_groups="form_name")
```