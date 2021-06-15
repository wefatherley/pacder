from http import client, server, HTTPStatus
from threading import Thread
from unittest import (
    defaultTestLoader, mock, TestCase, TextTestRunner
)
from urllib.parse import parse_qs, urlparse

from . import BaseConnector


RESPONSE_DATA = {
    "testpost": b"oh stop it you",
    "records": b'[{"patient_id": "p001"}]',
    "metadata":  b"""
        field_name,form_name,section_header,field_type,field_label,select_choices_or_calculations,field_note,text_validation_type_or_show_slider_number,text_validation_min,text_validation_max,identifier,branching_logic,required_field,custom_alignment,question_number,matrix_group_name,matrix_ranking,field_annotation
        patient_id,demographics,,text,"Patient ID",,"Scan the bottom QR code",,,,,,,,,,,@BARCODE-APP
    """.strip()
}


class MockAPIHandler(server.BaseHTTPRequestHandler):
    """Handler subclass for tests"""

    def do_POST(self):
        """Handle POST requests"""
        url = urlparse(self.path)
        query = parse_qs(url.query)

        # resources for testing pacder.connector.BaseConnector
        if url.path == "/test-base-connector":
            self.send_response(HTTPStatus.FOUND)
            self.writeheader("Location", "/redirected")
            self.end_headers()
        elif url.path == "/redirected":
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(RESPONSE_DATA["testpost"])
        
        # WIP resources for testing pacder.connector.BaseConnector
        elif url.path == "/redcap/api/":
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            
        # any other resource for testing both connectors
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


# test_suite = defaultTestLoader.loadTestsFromTestCase(TestBaseConnector)
# test_runner = TextTestRunner()
# test_runner.run(test_suite)
