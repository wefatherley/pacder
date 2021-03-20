"""WIP"""
from http import server, HTTPStatus
from logging import getLogger
from os import path
from shutil import copyfileobj
from urllib.parse import urlparse

from .core import *


LOGGER = getLogger(__name__)


PATH = path.dirname(__file__)
FRONTEND_HTML = open(PATH + "/static/service/frontend.html", "rb")
METADATA_HTML = open(PATH + "/static/service/metadata.html", "rb")
RECORDS_HTML = open(PATH + "/static/service/records.html", "rb")


class Service(server.BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html")
            self.end_headers()
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
