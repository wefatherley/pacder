"""pacder tests"""
from http import client, server, HTTPStatus
from threading import Thread
from unittest import (
    defaultTestLoader, mock, TestCase, TestRunner, TestSuite
)
from urllib.parse import parse_qs, urlparse


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
        url = parse.urlparse(self.path)
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

    @classmethod
    def setUpClass(cls):
        """Set up non-TLS base connector instance"""
        super().setUpClass()
        cls.base_conn = client.HTTPConnection
        cls.base_conn.__enter__ = BaseConnector.__enter__
        cls.base_conn.__exit__ = BaseConnector.__exit__
        cls.base_conn.post = BaseConnector.post
        cls.base_conn.method = "POST"

    @classmethod
    def tearDownClass(cls):
        """Set up base connector instance"""
        super().tearDownClass()
        if cls.base_conn.sock:
            cls.base_conn.close()

    def test_found(self):
        """Test redirection"""
        self.base_conn.path_stack.append("/test-base-connector")
        resp_bytes = self.base_conn.post(data="hello wrold!!")
        self.assertEqual(resp_bytes, RESPONSE_DATA["testpost"])

    def test_enter_exit(self):
        """Test context management"""
        self.base_conn.path_stack.append("/")
        self.base_conn.close()
        with self.base_conn as conn:
            resp = conn.post()
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)
        self.assertIsNone(self.base_conn.sock)


class TestConnector(WebTestCase):
    """Test Connector object"""

    @classmethod
    def setUpClass(cls):
        """Set up non-TLS base connector instance"""
        super().setUpClass()
        base_conn = client.HTTPConnection
        base_conn.__enter__ = BaseConnector.__enter__
        base_conn.__exit__ = BaseConnector.__exit__
        base_conn.post = BaseConnector.post        

    @classmethod
    def tearDownClass(cls):
        """Set up base connector instance"""
        super().tearDownClass()
        if cls.base_conn.sock:
            cls.base_conn.close()


class TestMetadata(TestCase):
    """Test Metadata object"""
    pass


class TestProject(WebTestCase):
    """Test Project object"""
    pass


class PacderTestSuite(TestSuite):
    """Gather and house test cases"""
    pass


test_suite = defaultTestLoader.loadTestsFromNames(
    [t for t in dir() if t.startswith("Test")]
)
test_runner = TextTestRunner()
