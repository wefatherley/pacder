"""pacder"""
from json import (loads as json_loads, dumps as json_dumps)
from logging import getLogger
from queue import Queue

from .connector import Connector
from .metadata import Metadata
from .record import Record


__all__ = ["Connector", "Metadata", "Project", "Record",]


LOGGER = getLogger(__name__) # TODO: logging


class Project:
    """container for REDCap project"""

    def __delitem__(self, key):
        """remove (delete) project resource"""
        pass

    def __enter__(self):
        """enter context"""
        if self.connector.sock is None:
            self.connector.connect()
        return self

    def __exit__(self, typ, val, trb):
        """exit context"""
        self.close()

    def __getitem__(self, key):
        """fetch (export) project resource"""
        if key == "metadata":
            def closed(proj=self, **kwargs):
                if not kwargs:
                    return proj.metadata
        elif key == "record":
            def closed(proj=self, **kwargs):
                with proj.connector as conn:
                    records = conn.records("export", **kwargs)
                return [
                    Record(r, project=proj)
                    for r in json_loads(records)
                ]
        return closed

    def __init__(self, host, path, token, **kwargs):
        """constructor"""
        self.connector = Connector(host, path, token)
        self.metadata = Metadata(project=self)
        self.autocommit = kwargs.get("autocommit", False)
        if not self.autocommit:
            self.request_queue = Queue()

    def __setitem__(self, key, value):
        """send (import) project resource"""
        if isinstance(value, (list, tuple, set)):
            value = "[" + ", ".join(str(r) for r in value) + "]"
        else:
            value = "[" + str(value) + "]"
        if self.autocommit:
            with self.connector as conn:
                conn.import_content(key, value)
        else:
            self.request_queue.put(("import_content", key, value))
            
    def close(self):
        """clean up self"""
        while self.request_queue.not_empty():
            task = self.request_queue.get()
            with self.connector as conn:
                resp = getattr(conn, task[0])(task[1], task[2])

    def factory(self, obj):
        """return a pacder object (i.e. REDCap abstraction)"""
        if obj == "record":
            return Record(project=self)
        else:
            raise NotImplemented
