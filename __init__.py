"""WIP"""
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from os import path
from shutil import copyfileobj

from .core import *


LOGGER = getLogger(__name__)


MY_NAME = path.dirname(__file__)
FRONTEND_HTML_PATH = MY_NAME + "/static/frontend.html"
METADATA_HTML_PATH = MY_NAME + "/static/metadata.html"
RECORDS_HTML_PATH = MY_NAME + "/static/records.html"


class Service(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html")
            self.end_headers()
            copyfileobj(open(FRONTEND_HTML_PATH, "rb"), self.wfile)
        elif self.path == "/metadata":
            pass
        elif self.path == "/records":
            pass
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


class Project: pass