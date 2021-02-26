"""Connector objects"""
from http import client, HTTPStatus
from io import BytesIO, IOBase
from logging import getLogger
from urllib.parse import urlencode


LOGGER = getLogger(__name__)


class BaseConnector(client.HTTPSConnection):
    """HTTP methods container"""

    path_stack = list()
    delete_headers = {}
    export_headers = {}
    import_headers = {}

    def __enter__(self):
        """Enter context"""
        if self.sock is None:
            self.connect()
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.close()
    
    def post(self, data):
        """Handles POST procedure. Returns HTTPResponse object"""
        try:
            self.putrequest(method=self.method, url=self.path_stack[-1])
            for k,v in self.effective_headers.items():
                self.putheader(k,v)
            self.endheaders(message_body=data)
        except Exception as e:
            # TODO: perform certain retries
            LOGGER.error("request threw exception: exc=%s", e)
            return None
        else:
            response = self.getresponse()
            response.headers = {k.lower(): v for k,v in response.headers}
            if response.status == HTTPStatus.OK:
                LOGGER.info(
                    "response received sucessfully: octets=%s",
                    response.headers.get("content-length", "NA")
                )
                if self.path_stack[-1] != self.path_stack[0]:
                    self.path_stack.append(self.path_stack[0])
                return response
            else: #(
            #     HTTPStatus.MULTIPLE_CHOICES
            #     <= response.status <
            #     HTTPStatus.BAD_REQUEST
            # ):
            #     # TODO: perform certain retries
            #     LOGGER.info(
            #         "following redirect: link=%s",
            #         response.headers.get("link")
            #     )
            #     redirect_path = self.parse_link_header(
            #         response.headers.get("link")
            #     )
            #     self.path_stack.append(redirect_path)
            #     return self.post(request)
            # elif (
            #     HTTPStatus.BAD_REQUEST
            #     <= response.status <=
            #     HTTPStatus.INTERNAL_SERVER_ERROR
            # ):
            #     # TODO: perform certain retries
            #     LOGGER.error(
            #         "bad request: status=%i, reason=%s",
            #         response.status, response.reason
            #     )
            #     return None
            # elif HTTPStatus.INTERNAL_SERVER_ERROR <= response.status:
                # TODO: perform certain retries
                LOGGER.error(
                    "API issues: status=%i, reason=%s",
                    response.status, response.reason
                )
                return None

    def prepare_data(self, data):
        """Set a file-like body"""
        if isinstance(data, (dict, list, tuple)):
            data = BytesIO(urlencode(data).encode("latin-1"))
        if not isinstance(data, IOBase):
            raise RuntimeError("Unable to build body")
        return data

    def set_effective_headers(self, action):
        if action == "delete":
            self.effective_headers = self.delete_headers
        elif action == "export":
            self.effective_headers = self.export_headers
        elif action == "import":
            self.effective_headers = self.import_headers
        else:
            raise RuntimeError("No such action :/")
            
    def parse_link_header(self, header):
        """Returns a URL from link header value"""
        raise NotImplementedError


class Connector(BaseConnector):
    """REDCap methods container"""

    def __init__(self, host, path, token):
        """Construct API wrapper"""
        if path is None or token is None:
            raise RuntimeError("path and/or token required")
        self.path_stack.append(path)
        self.token = token
        self.method = "POST"
        super().__init__(host)

    def delete_resource(self, resource, **parameters):
        """WIP"""
        pass

    def export_resource(self, resource, path=None, **parameters):
        """WIP"""
        pass

    def import_resource(self, resource, data, **parameters):
        """WIP"""
        pass
        
    def arms(self, action, data=None, **parameters):
        pass

    def events(self, action, data=None, **parameters):
        """WIP"""
        pass

    def field_names(self, action, data=None, **parameters):
        """WIP"""
        pass

    def files(self, action, data=None, **parameters):
        """WIP"""
        pass

    def instruments(self, action, data=None, **parameters):
        """WIP"""
        pass

    def metadata(self, action, data=None, **parameters):
        """WIP"""
        pass

    def projects(self, action, data=None, **parameters):
        """WIP"""
        pass

    def records(self, action, data=None, **parameters):
        """WIP"""
        pass
        
    def repeating_ie(self, action, data=None, **parameters):
        """WIP"""
        pass

    def reports(self, action, data=None, **parameters):
        """WIP"""
        pass

    def redcap(self, action, data=None, **parameters):
        """WIP"""
        pass

    def surveys(self, action, data=None, **parameters):
        """WIP"""
        pass

    def users(self, action, data=None, **parameters):
        """WIP"""
        pass


__all__ = ["Connector",]
