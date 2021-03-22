.. pacder documentation master file, created by
   sphinx-quickstart on Sun Mar 21 16:39:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**pacder**: exposes the REDCap API
==================================

`REDCap <http://www.project-redcap.org>`_ is a robust electronic data capture platform built by Vanderbilt University. This package contains tools for interacting with a REDCap instance, via the REDCap API. Central to the API are three core *actions*, **delete**, **export**, and **import**, each of which permit an external application to interact via HTTP with a *project* residing in the REDCap instance. The external application might for example be an interview/experiment/... client that investigators use to collect project data, or it could be a client that crawls the data of project, or any other such thing.

The aim of this package is to expose through the Python programming langauge the REDCap API. Usage generally exists at two different layers. At the low level, interaction with a REDCap project can be performed with the :class:`Connector` object, which returns raw response data as bytes::

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
      delete_bytes = conn.delete_content("files", name="virus.png")
      # or, identically,
      delete_bytes = conn.files("delete", name="virus.png")

      # fetch some records
      records_bytes = conn.export_content("records", format="csv", filterLogic="[age] > 30", ...)
      # or, with JSON formatting
      records_bytes = conn.records("export", format="json", filterLogic="[age] > 30", ...)

      # update a project's metadata
      with open("project_metadata.csv", "r") as fp:
         import_bytes = conn.import_content("metadata", fp)
         # or, identically,
         import_bytes = conn.metadata("import", fp)

The :class:`Connector` object provides enough logic to handle tasks like writing a CSV file of records or metadata. It is also possible to perform more "atomic" inspections of, e.g., a record set by going like ``json.loads(records_bytes.decode("latin-1"))``.

However, since most record data come through as a string in this circumstance (i.e. a date), they will invariably lack comparison operators, which isn't very useful. Nonetheless, if the project has metadata that specifies appropriate typing for such record data, this package also provides a higher-level interface, the :class:`Project` object. This object furnishes type-casting based on the project metadata, much like an ORM, and has other useful features::

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

      # update project by adding a new/replacement field
      proj.metadata["vaccine_manufacturer"] = {"field_type": "radio", ...}
      # hide an existing/replaced field
      proj.metadata["vaccine"]["field_annotation"] = "@HIDDEN"

      # create a SQL migration from project metadata for auxiliary relational datastore
      proj.sql_migration("/migrations/myproject.sql")
      # by default the migration has tables that go by field type,
      # but they can be made to go by, e.g., form name
      proj.sql_migration("/migrations/myproject.sql", table_groups="form_name")

.. toctree::
   :maxdepth: 2

   reference

