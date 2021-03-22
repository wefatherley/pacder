Reference
=========

Here the package modules are described.

:mod:`connector` - Connector objects
------------------------------------

To interact with the API of a REDCap instance, it is necessary to utilize a "web client" that can perform network I/O and HTTP parsing. This module defines classes that perform such I/O and parsing.

.. class:: BaseConnector(http.client.HTTPSConnections)

   This class performs the logic related to network I/O and HTTP parsing. It is designed to be subclassed/inhereted, but can be instantiated with it's parent constructor for purposes unrelated to normal usage of this package. Ordinarily, it is not instantiated directly by a user. It has the following members:


   .. method:: BaseConnector.__enter__()

      Satifies the context-manager protocol. Prior to returning the instance, this method will attempt to open the instance's socket if closed.


   .. method:: BaseConnector.__exit__(typ, val, trb)

      Satisfies the context-manager protocol. Prior to exiting the conext, this method will close the instance's socket.


   .. method:: BaseConnector.post(data=None)

      Performs the HTTP request. If the action is to ``import`` content, ``data`` should be a file-like object. For ``delete`` and ``export`` actions, data is left as default in subclasses.


   .. method:: BaseConnector.set_effective_headers(action)

      Called by ``BaseConnector.post`` to set request headers based on the effective action.


   .. method:: BaseConnector.parse_link_header(header)

      Called on redirect response by ``BaseConnector.post`` to extract and set effective the link URL. Currently not implemented.


.. class:: Connector(BaseConnector)

   This class is the "public" interface for a REDCap instance. It inherets all the members of it's parents. It expects string arguments ``host``, ``path``, and ``token``, which are along the lines of ``redcap.myorg.net``, ``/path/to/api/dir``, and ``jgHA12K3dgkKLQ95548...``, respectively. Members include:

   .. method:: __init__(host, path, token)

      Constructs the instance by setting various attributes, and calling it's parent's parent. When using this object without the context manager protocol (i.e. like ``conn = Connector(...)``), be sure to close it afterward (i.e. ``conn.close()``).

   .. method:: delete_content(**parameters)
   .. method:: export_content(**parameters)
   .. method:: import_content(data, **parameters)

      These methods expose the three "actions" that can be performed against the REDCap API. They do not verify if the user has supplied the correct parameters, be sure to have error messages returned from the API in the desired format. All three members return response data as ``latin-1`` bytes. Usage is like::

         import json


         with Connector(myhost, mypath, mytoken) as conn:
            
            # ignoring the response bytes
            conn.delete(content="record", filterLogic="[age] > 35")

            # fetch and load up the project metadata
            metadata = json.loads(conn.export(content="metadata").decode("latin-1"))

            # upload a picture (again ignoring response bytes)
            with open("bork.png", "rb") as fp:
               conn.import_content(data=fp, content="files")

      As mentioned in the snippet comments, it's always ok to call one of these members without assignment, but this choice is at the expense of understanding any return information. For instance, in importing records, the response does contain useful information related to the success and failure of the import.


   .. method:: arms(action, data=None, **parameters)
   .. method:: events(action, data=None, **parameters)
   .. method:: field_names(action, data=None, **parameters)
   .. method:: files(action, data=None, **parameters)
   .. method:: instruments(action, data=None, **parameters)
   .. method:: metadata(action, data=None, **parameters)
   .. method:: projects(action, data=None, **parameters)
   .. method:: records(action, data=None, **parameters)
   .. method:: repeating_ie(action, data=None, **parameters)
   .. method:: reports(action, data=None, **parameters)
   .. method:: redcap(action, data=None, **parameters)
   .. method:: surveys(action, data=None, **parameters)
   .. method:: users(action, data=None, **parameters)

      These methods alias the three action members described above, and are passed an action name string as the only inline parameter. The ``data`` parameter is passed a file-like object, and is used for the import action.


   Note for :class:`Connector` instances that there are a few attributes that are useful in various contexts. For example, to have a look at all the API requests made, ``Connector.path_stack`` contains an ordered list of request URLs.


:mod:`metadata` - Metadata object
---------------------------------

<<<<<<< HEAD
A project's metadata (a.k.a. data dictionary) is the defining feature of the project itself, and houses important information related to the typing, validation, and overall characteristics of project records. This module defines a class, :class:`Metadata`, that makes Pythonic the columns of a project's metadata, and also provides several convience methods for external application development.

.. class:: Metadata(raw_metadata, raw_field_names)

   This class is the "public" interface to a REDCap project's metadata. As a container emulator, a given project field is accessible in the same manner as accessing the values of a dictionary. 
=======
A project's metadata (a.k.a. data dictionary) is the defining feature of the project itself, and houses important information related to the typing and validation of project records. This module defines objects that parse, construct, and utilize such typing and validation information.

.. class:: Metadata

   This class provides a dictionary-like interface to a REDCap project's metadata. It is designed to be instantiated with metadata and export-field-name JSON arrays, be them raw bytes, a string, or loaded as a list of dictionaries.
>>>>>>> 1040fe24cbf2156c051bfa7b8fbc3f25fbf3b5b5


:mod:`util` - Utility objects
-----------------------------

The module defines data structures used by other modules in the package.
