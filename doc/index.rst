.. pacder documentation master file, created by
   sphinx-quickstart on Sun Mar 21 16:39:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**pacder**: exposes the REDCap API
==================================

`REDCap <http://www.project-redcap.org>`_ is a robust electronic data capture platform built by Vanderbilt University. This package contains tools for interacting with a REDCap instance, via the REDCap API. The REDCap API is composed of three *actions*, **delete**, **export**, and **import**, each of which permit an external application to interact via HTTP with a *project* residing in the REDCap instance. The external application might for example be an interview/experiment/... client that investigators use to collect project data, be it human interview responses or chemical instrumentation data. Further, the external application could be a client that crawls through data of multiple projects to ensure good practices, or any other such thing.

The aim of this package is to expose through the Python programming langauge the REDCap API, and enable developers to write external applications that interact with REDCap instances with the widest possible scope. On one hand, all that is necessary to wrap the REDCap API is a HTTP client that can perform the three actions for any REDCap content. On the other hand, REDCap projects are nuanced enough to limit rapid or robust development of external applications-- project records returned by a vanilla HTTP client will contain data whose native typing is masked by their string representation; project metadata will contain, e.g., branching logic that, as returned by a vanilla HTTP client, cannot be evaluated by Python; and so on. To address these nuances, ``pacder`` exposes the REDCap API with two abstraction layers. At the low level, interaction with a REDCap project can be performed with the :class:`Connector` object, a "vanilla HTTP client", which returns response data as bytes::

   # First, find your API location/credentials, e.g.,
   from os import getenv

   host = getenv["REDCAP_HOST"] # e.g. redcap.myorg.net
   path = getenv["REDCAP_PATH"] # e.g. /apps/redcap/api/
   token = getenv["REDCAP_PROJECT123_TOKEN"] # e.g. sf11gk2herg3o34d...


   # import the connector object
   from pacder import Connector

   # use connector object as a context manager (or not)
   with Connector(host, path, token) as conn:

      # specify format of data (defaults to JSON)
      conn.format = "csv"
      # a `format` parameter can also be passed into the below functions
      # see the reference for more information

      # remove a file from the project
      delete_bytes = conn.delete_content("files", name="virus.png")
      # or, identically,
      delete_bytes = conn.files("delete", name="virus.png")

      # fetch some records
      records_bytes = conn.export_content("records", filterLogic="[age] > 30", ...)
      # or, identically,
      records_bytes = conn.records("export", filterLogic="[age] > 30", ...)

      # update a project's metadata
      with open("project_metadata.csv", "r") as fp:
         import_bytes = conn.import_content("metadata", fp)
         # or, identically,
         import_bytes = conn.metadata("import", fp)

The :class:`Connector` object provides enough logic in conjunction with the Python ecosystem to handle tasks like writing a CSV file of records or metadata, importing such data, or deleting it, or to perform more "atomic" albeit type-naive inspections of, e.g., a record set by going like ``json.loads(records_bytes.decode("latin-1"))``.

To furnish external applications with more logic and tools for working on REDCap data, ``pacder`` also provides a higher-level interface, the :class:`Project` object. This object exposes the REDCap API also, but acts more like an ORM::

   from datetime import date

   from pacder import Project

   # use project object as a context manager (or not)
   with Project(host, path, token) as proj:

      # export, inspect records Pythonically
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

      # create a SQL migration from project metadata
      proj.sql_migration("/migrations/myproject.sql")
      # by default the migration has tables that go by field type,
      # but they can be made to go by, e.g., form name
      proj.sql_migration("/migrations/myproject.sql", table_groups="form_name")

As seen above :class:`Project` has a few of it's own convenience methods, like ``Project.records`` for fetching records, but it also has as attributes a :class:`Connector` instance at ``Project.connector``, and project metadata abstraction at ``Project.metadata``. For more information on this attribute, see :class:`Metadata`.

.. toctree::
   :maxdepth: 2

   reference

