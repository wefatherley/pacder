"""WIP"""
from http import server, HTTPStatus
from logging import getLogger
from os import path
from shutil import copyfileobj
from urllib.parse import urlparse

from .core import *


LOGGER = getLogger(__name__)


PATH = path.dirname(__file__)
FRONTEND_HTML_PATH = PATH + "/static/service/frontend.html"
METADATA_HTML_PATH = PATH + "/static/service/metadata.html"
RECORDS_HTML_PATH = PATH + "/static/service/records.html"


class Service(server.BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html")
            self.end_headers()
            copyfileobj(open(FRONTEND_HTML_PATH, "rb"), self.wfile)
        elif self.path == "/metadata":
            self.send_error(HTTPStatus.NOT_FOUND)
        elif self.path == "/records":
            self.send_error(HTTPStatus.NOT_FOUND)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)
