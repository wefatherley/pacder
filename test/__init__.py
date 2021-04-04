"""pacder tests"""
from http import server, HTTPStatus
from threading import Thread
from unittest import (
    mock, TestCase, TestLoader, TestRunner, TestSuite, TestResult
)
from urllib.parse import parse_qs, urlparse

from .. import *


RESPONSE_DATA = {
    "testpost": b"oh stop it you",
    "records": b'[{"patient_id": "p001"}]',
}

TEST_METADATA = """
field_name,form_name,section_header,field_type,field_label,select_choices_or_calculations,field_note,text_validation_type_or_show_slider_number,text_validation_min,text_validation_max,identifier,branching_logic,required_field,custom_alignment,question_number,matrix_group_name,matrix_ranking,field_annotation
patient_id,demographics,,text,"Patient ID",,"Scan the bottom QR code",,,,,,,,,,,@BARCODE-APP
""".strip()




class MockAPIHandler(server.BaseHTTPRequestHandler):
    """Service subclass for tests"""

    def do_POST(self):
        """Handle POST requests"""
        url = parse.urlparse(self.path)
        query = parse_qs(url.query)
        if self.path == "/testpost":
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(RESPONSE_DATA["testpost"])
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
        t = Thread(target=cls.service.serve_forever)
        t.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down HTTP server"""
        cls.service.shutdown()


class TestBaseConnector(WebTestCase):
    """Test BaseConnector object"""
    
    def test_post(self):
        """Test below app-layer"""
        bconn = BaseConnector
        bconn.method = "POST"
        bconn.pathstack.append("/testpost")
        with bconn("127.0.0.1") as tconn:
            resp_bytes = tconn.post(data="hello wrold!!")
            self.assertEqual(resp_bytes, b"oh stop it you")

    def test_redirect(self):
        with Connector("127.0.0.1", "/testredirect", "foo"):
            pass


class TestConnector(WebTestCase):
    """Test Connector object"""
    pass


class TestMetadata(TestCase):
    """Test Metadata object"""
    pass


class TestProject(WebTestCase):
    """Test Project object"""
    pass


class PacderTestSuite(TestSuite):
    """Gather and house test cases"""
    pass



test_runner, test_suite = None, None