"""redcapp tests"""
from http import client, server, HTTPStatus
from threading import Thread
from unittest import mock, TestCase

from .. import Service


class TestService(Service):
    """Service subclass for tests"""

    def do_POST(self):
        """Handle POST requests"""
        url = urlparse(self.path)
        if url.path == "/tests":
            pass
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


class BaseWebTest(TestCase):
    """Base class for web-related tests"""

    @classmethod
    def setUpClass(cls):
        """Set up HTTP server"""
        cls.service = server.ThreadingHTTPServer(
            ("127.0.0.1", 8080), TestService
        )
        t = threading.Thread(target=cls.service.serve_forever)
        t.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down HTTP server"""
        cls.service.shutdown()


class TestClient(BaseWebTest):
    """Test core.Connector"""
    
    def test_BaseConnector(self):
        pass

    def test_Connector(self):
        pass


class TestMetadata(TestCase):
    """Test core.Metadata"""
    pass


class TestProject(BaseWebTest):
    """Test core.Project"""
    pass


class TestRecord(TestCase):
    """Test core.Project"""
    pass


class TestService(BaseWebTest):
    """Test HTTP core.Service"""

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
