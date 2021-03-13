# pacder: Python's REDCap API wrapper
This Python 3 package furnishes programmatic access to a REDCap instance's API, allowing token holders to __delete__, __export__, and __import__ content related to one or more of their. At the moment it also exposes through it's CLI a loopback webserver that makes creating/altering/removing/inspecting REDCap abstractions like _metadata_ and _records_ from a particular project easy.

## Install
Available for __Python 3.6+__. There are no dependencies other than the Python standard library. 

Install the latest stable release with `pip`:

`python3 -m pip install pacder`,

or with `conda`:

`conda install -c pacder`.

## Usage
For programmatic API access, use objects residing in `core`:

`from pacder import core as rc` or `import pacder.core as rc`

At the lowest level, `rc` exposes a REDCap project with the `Connector` object:

```python
from os import getenv

host = getenv["REDCAP_HOST"] # e.g. redcap.myorg.net
path = getenv["REDCAP_PATH"] # e.g. /apps/redcap/api/
token = getenv["REDCAP_PROJECT123_TOKEN"] # e.g. sf11gk2herg3o34d...


# use connector object as a context manager (or not)
with rc.Connector(host, path, token) as conn:

    # remove a file from the project
    conn.delete_content("files", name="flowers.png")
    # or, identically,
    conn.files("delete", name="flowers.png")

    # fetch some records
    my_records = conn.export_content("records", format="csv", filterLogic="[age] > 30")
    # or, identically,
    my_records = conn.records("export", format="csv", filterLogic="[age] > 30")
    # and similar syntax for exporting other content...

    # update a project's metadata
    with open("project_metadata.csv", "r") as fp:
        conn.import_content("metadata", fp)
        # or, identically,
        conn.metadata("import", fp)
        # and similar syntax for importing other content...
```

