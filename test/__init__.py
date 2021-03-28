"""pacder tests"""
from http import server, HTTPStatus
from threading import Thread
from unittest import mock, TestCase
from urllib.parse import parse_qs, urlparse

from .. import *


RESPONSE_DATA = {
    "records": b'[{"patient_id": "p001"}]',
}


class MockAPIHandler(server.BaseHTTPRequestHandler):
    """Service subclass for tests"""

    def do_POST(self):
        """Handle POST requests"""
        url = parse.urlparse(self.path)
        query = parse_qs(url.query)
        if query["content"] == "records":
            self.send_response(HTTPStatus.OK)
            self.send_header(
                "content-type", "text/{}".format(query["format"])
            )
            self.end_headers()
            self.wfile.write(RESPONSE_DATA[query["content"]])
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


class WebTestCase(TestCase):
    """Base class for web-related tests"""

    @classmethod
    def setUpClass(cls):
        """Set up HTTP server"""
        cls.service = server.ThreadingHTTPServer(
            ("127.0.0.1", 8080), MockAPIHandler
        )
        t = threading.Thread(target=cls.service.serve_forever)
        t.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down HTTP server"""
        cls.service.shutdown()


class TestClient(WebTestCase):
    """Test core.Connector"""
    
    def test_BaseConnector(self):
        pass

    def test_Connector(self):
        pass

    def test_redirection(self):
        pass


class TestMetadata(TestCase):
    """Test core.Metadata"""
    pass


class TestProject(WebTestCase):
    """Test core.Project"""
    pass

test_runner, test_suite = None, None