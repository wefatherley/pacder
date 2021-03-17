# WIP pacder
Exposes REDCap's API through the Python programming langauge, allowing token holders to __delete__, __export__, and __import__ content related to one or more of their projects, develop ETL flows, project analyses, interview clients, and more.
## Install
Available for __Python 3.6+__.

Install the latest stable release with `pip`:

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
    conn.delete_content("files", name="flowers.png")
    # or, identically,
    conn.files("delete", name="flowers.png")

    # fetch some records (a list of dicts)
    my_records = conn.export_content("records", format="csv", filterLogic="[age] > 30", ...)
    # or, identically,
    my_records = conn.records("export", format="csv", filterLogic="[age] > 30", ...)

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

        # get the original field name of a checkbox variable
        comorbids_ofn = record["comorbid___123"].original_field_name

        # perform temporal comparisons
        if record["sign_up_date"].value < date(2021, 5, 1):
            print("{} signed up too early!!".format(record["name"].value))

        # make decisions based on a record's branching logic
        if record["available_vaccine_sites"].logic:
            print("{} saw vax sites!!".format(record["name"].value))

    # add a field to the project metadata
    proj.metadata["vaccine_manufacturer"] = {"field_type": "radio", ...}
    # hide an existing field
    proj.metadata["vaccine"]["field_annotation"] = "@HIDDEN"
    # update the redcap instance
    proj.sync()

    # create a SQL migration from project metadata for auxiliary relational datastore
    proj.sql_migration("/migrations/myproject.sql")
    # by default the migration has tables that go by field type,
    # but they can be made to go by, e.g., form name
    proj.sql_migration("/migrations/myproject.sql", table_groups="form_name")
```
Please review the reference documentation for more usage information.
### Graphical usage
In addition to usage in a computer program, `pacder` also exposes through the command line a simple loopback server that serves a graphical tool for exploring records, editing metadata, and so on. Simply open the terminal and execute `python3 -m pacder run`, open a browser and visit the loopback address at port `8080`, i.e., `http://127.0.0.1:8080/`.