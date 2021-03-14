"""Connector objects"""
from http import client, HTTPStatus
from io import BytesIO
from logging import getLogger
from urllib.parse import urlencode


LOGGER = getLogger(__name__)


PARAMETERS = []


class BaseConnector(client.HTTPSConnection):
    """HTTP methods container"""

    path_stack = []
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
        """Handle HTTP POST procedure"""
        try:
            self.putrequest(
                method=self.method, url=self.path_stack[-1]
            )
            for k,v in self.effective_headers.items():
                self.putheader(k,v)
            self.endheaders(message_body=data)
        except Exception as e:
            # TODO: perform certain retries
            LOGGER.error("request threw exception: exc=%s", e)
            return None
        else:
            response = self.getresponse()
            response.headers = {
                k.lower(): v for k,v in response.headers
            }
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
                return response.status, ""

    def prepare_data(self, data):
        """Return request-ready data"""
        if isinstance(data, (dict, list, tuple)):
            return BytesIO(urlencode(data).encode("latin-1"))
        elif isinstance(data, str):
            return BytesIO(data.encode("latin-1"))
        raise Exception("Unable to build body")

    def set_effective_headers(self, action):
        """Set the request, or "effective" headers"""
        if action == "delete":
            self.effective_headers = self.delete_headers
        elif action == "export":
            self.effective_headers = self.export_headers
        elif action == "import":
            self.effective_headers = self.import_headers
            
    def parse_link_header(self, header):
        """Returns URLs from link header"""
        raise NotImplementedError


class Connector(BaseConnector):
    """WIP REDCap methods container"""

    def __init__(self, host, path, token):
        """Construct API wrapper"""
        if path is None or token is None:
            raise RuntimeError("path and/or token required")
        self.path_stack.append(path)
        self.params = "token={}".format(token)
        self.method = "POST"
        super().__init__(host)

    def delete_content(self, **parameters):
        """Delete content"""
        if data in parameters:
            LOGGER.warn("Cannot pass in data on Delete")
            del parameters[data]
        params = self.params
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            params += "&{}={}".format(key, value)
        params = params.encode("latin-1")
        self.set_effective_headers("delete")
        status, data = self.post(params)
        LOGGER.info(
            "delete resource: status=%i, content=%s",
            status,
            parameters["content"]
        )
        return data
        
    def export_content(self, **parameters):
        """Export content"""
        if data in parameters:
            LOGGER.warn("Cannot pass in data on Export")
            del parameters[data]
        params = self.params
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            params += "&{}={}".format(key, value)
        params = params.encode("latin-1")
        self.set_effective_headers("export")
        status, data = self.post(params)
        LOGGER.info(
            "export resource: status=%i, content=%s",
            status,
            parameters["content"]
        )
        return data

    def import_content(self, data, **parameters):
        """Import content"""
        params = self.params
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            params += "&{}={}".format(key, value)
        self.path_stack.append(self.path_stack[0] + "?" + params)
        self.set_effective_headers("import")
        status, data = self.post(self.prepare_data(data))
        LOGGER.info(
            "import resource: status=%i, content=%s",
            status,
            parameters["content"]
        )
        return data
        
    def arms(self, action, data=None, **parameters):
        """Modify arms"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="arms", **parameters
        )

    def events(self, action, data=None, **parameters):
        """Modify events"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="events", **parameters
        )

    def field_names(self, action, data=None, **parameters):
        """Modify field_names"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="field_names", **parameters
        )

    def files(self, action, data=None, **parameters):
        """Modify files"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="files", **parameters
        )

    def instruments(self, action, data=None, **parameters):
        """Modify instruments"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="instruments", **parameters
        )

    def metadata(self, action, data=None, **parameters):
        """Modify metadata"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="metadata", **parameters
        )

    def projects(self, action, data=None, **parameters):
        """Modify projects"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="projects", **parameters
        )

    def records(self, action, data=None, **parameters):
        """Modify records"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="records", **parameters
        )
        
    def repeating_ie(self, action, data=None, **parameters):
        """Modify repeating_ie"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="repeating_ie", **parameters
        )

    def reports(self, action, data=None, **parameters):
        """Modify reports"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="reports", **parameters
        )

    def redcap(self, action, data=None, **parameters):
        """Modify redcap"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="redcap", **parameters
        )

    def surveys(self, action, data=None, **parameters):
        """Modify surveys"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="surveys", **parameters
        )

    def users(self, action, data=None, **parameters):
        """Modify users"""
        return getattr(self, "{}_content".format(action))(
            data=data, content="users", **parameters
        )


__all__ = ["Connector",]
