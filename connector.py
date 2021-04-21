"""Connector objects """
from http import client, HTTPStatus
from io import IOBase
from logging import getLogger
from urllib.parse import urlencode


LOGGER = getLogger(__name__)


PARAMETERS = []

DELETE_HEADERS = {}
EXPORT_HEADERS = {}
IMPORT_HEADERS = {}


class BaseConnector(client.HTTPSConnection):
    """HTTP methods container"""

    path_stack = []

    def __enter__(self):
        """Enter context"""
        if self.sock is None:
            self.connect()
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.close()
    
    def post(self, data=None):
        """Handle HTTP POST procedure"""
        try:
            self.putrequest(
                method=self.method, url=self.path_stack[-1]
            )
            if isinstance(data, IOBase):
                data = bytes(data.read(), "latin-1")
            elif isinstance(data, str):
                data = open(data, "rb").read()
            elif data is not None and not isinstance(data, bytes):
                raise Exception("Can't POST data")
            for k,v in self.effective_headers.items():
                self.putheader(k,v)
            if data is not None:
                self.putheader("content-length", len(data))
            self.endheaders(message_body=data)
        except Exception as e:
            LOGGER.exception("request threw exception: exc=%s", e)
            if isinstance(e, client.NotConnected):
                try:
                    LOGGER.info("trying to reconnect")
                    self.connect()
                    self.post(data=data)
                except client.NotConnected:
                    LOGGER.error("unable to connect")
                    raise
        else:
            response = self.getresponse()
            response.headers = {
                k.lower(): v for k,v in response.getheaders()
            }
            if (
                HTTPStatus.OK
                <= response.status <
                HTTPStatus.MULTIPLE_CHOICES
            ):
                LOGGER.info(
                    "response received sucessfully: octets=%s",
                    response.headers.get("content-length", "NA")
                )
                return response
            elif (
                HTTPStatus.MULTIPLE_CHOICES
                <= response.status <
                HTTPStatus.BAD_REQUEST
            ):
                resp_data = response.read().decode("latin-1")
                LOGGER.info(
                    "following redirect: link=%s, resp_data=%s",
                    response.headers.get("location"),
                    resp_data
                )
                self.path_stack.append(
                    response.headers.get("location")
                )
                self.post(data=data)
            elif response.status >= HTTPStatus.BAD_REQUEST:
                # 400s and 500s compacted into one elif for now
                # TODO: perform certain retries
                # TODO: verify REDCap exceptions are tied to 400s/500s
                LOGGER.error(
                    "erroneous request: status=%i, reason=%s",
                    response.status, response.reason
                )
                return response

    def set_effective_headers(self, action):
        """Set the request, or "effective" headers"""
        if action == "delete":
            self.effective_headers = DELETE_HEADERS
        elif action == "export":
            self.effective_headers = EXPORT_HEADERS
        elif action == "import":
            self.effective_headers = IMPORT_HEADERS
            

class Connector(BaseConnector):
    """WIP REDCap methods container"""

    delete_params = {}
    export_params = {}
    import_params = {}

    def __init__(self, host, path, token):
        """Construct API wrapper"""
        if path is None or token is None:
            raise RuntimeError("path and/or token required")
        self.path_stack.append(path)
        self.method = "POST"
        super().__init__(host)
        self.delete_params["token"] = token
        self.export_params["token"] = token
        self.import_params["token"] = token

    def build_params(self, action, content, **parameters):
        """Build urlencoded query"""
        if "data" in parameters:
            raise Exception("Cannot pass data in parameters")
        params = getattr(self, "{}_params".format(action))
        params["content"] = content
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            params[key] = value
        return params

    def delete_content(self, content, **parameters):
        """Delete content"""
        params = build_params("delete", content, **parameters)
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("delete")
        resp = self.post()
        LOGGER.info(
            "delete resource: status=%i, content=%s",
            resp_status,
            parameters["content"]
        )
        return resp.read()
        
    def export_content(self, content, **parameters):
        """Export content"""
        params = build_params("export", content, **parameters)
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("export")
        resp = self.post()
        LOGGER.info(
            "export resource: status=%i, content=%s",
            resp_status,
            parameters["content"]
        )
        return resp.read()

    def import_content(self, data, **parameters):
        """Import content"""
        params = build_params("import", content, **parameters)
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("import")
        resp = self.post(data)
        LOGGER.info(
            "import resource: status=%i, content=%s",
            resp_status,
            parameters["content"]
        )
        return resp.read()
        
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
