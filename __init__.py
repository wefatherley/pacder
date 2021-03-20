"""WIP"""
from http import server, HTTPStatus
from logging import getLogger
from os import path
from shutil import copyfileobj
from urllib.parse import urlparse

from .core import *


LOGGER = getLogger(__name__)


PATH = path.dirname(__file__)
<<<<<<< HEAD
FRONTEND_HTML = open(PATH + "/static/service/frontend.html", "rb")
METADATA_HTML = open(PATH + "/static/service/metadata.html", "rb")
RECORDS_HTML = open(PATH + "/static/service/records.html", "rb")
=======
FRONTEND_HTML_PATH = PATH + "/static/service/frontend.html"
METADATA_HTML_PATH = PATH + "/static/service/metadata.html"
RECORDS_HTML_PATH = PATH + "/static/service/records.html"
>>>>>>> 6c5ac173826e2e4aa7baddd4aab80a0c7cd37575


class Service(server.BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            fp = open(FRONTEND_HTML_PATH, "rb")
        elif self.path == "/metadata":
            fp = open(METADATA_HTML_PATH, "rb")
        elif self.path == "/records":
            fp = open(RECORDS_HTML_PATH, "rb")
        else: fp = None
        if fp is not None:
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html")
            self.end_headers()
<<<<<<< HEAD
            copyfileobj(FRONTEND_HTML, self.wfile)
            LOGGER.info(
                "get index: remote_addr=%s", self.client_address
            )
        elif self.path == "/metadata":
            pass
        elif self.path == "/records":
            pass
        else:
            self.send_error(HTTPStatus.NOT_FOUND)
=======
            copyfileobj(fp, self.wfile)
        else: self.send_error(HTTPStatus.NOT_FOUND)
        
>>>>>>> 6c5ac173826e2e4aa7baddd4aab80a0c7cd37575
