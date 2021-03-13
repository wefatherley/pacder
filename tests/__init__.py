"""redcapp tests"""
from http import client, server, HTTPStatus
from threading import Thread
from unittest import mock, TestCase

from .. import Service


class TestClient(TestCase):
    """Test core.connector"""
    pass


class TestMetadata(TestCase):
    """Test core.metadata"""
    pass


class TestProject(TestCase):
    """Test core.Project"""
    pass


class TestService(TestCase):
    """Test HTTP services"""

    @classmethod
    def setUpClass(cls):
        """Set up HTTP server"""
        cls.service = server.ThreadingHTTPServer(
            ("127.0.0.1", 8080), Service
        )
        t = threading.Thread(target=cls.service.serve_forever)
        t.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down HTTP server"""
        cls.service.shutdown()

    def test_DELETE(self):
        """Test URLs that support DELETE"""
        pass

    def test_GET(self):
        """Test URLs that support GET"""
        pass

    def test_POST(self):
        """Test URLs that support POST"""
        pass

    def test_PUT(self):
        """Test URLs that support PUT"""
        pass

