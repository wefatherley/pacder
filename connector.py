"""Connector objects """
from http import client, HTTPStatus
from logging import getLogger


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
    
    def post(self, data=None):
        """Handle HTTP POST procedure"""
        try:
            self.putrequest(
                method=self.method, url=self.path_stack[-1]
            )
            for k,v in self.effective_headers.items():
                self.putheader(k,v)
            self.endheaders(message_body=data)
        except Exception as e:
            LOGGER.exception("request threw exception: exc=%s", e)
            if isinstance(e, client.NotConnected):
                try:
                    LOGGER.info("reconnecting")
                    self.connect()
                    self.post(data=data)
                except client.NotConnected:
                    LOGGER.error("unable to connect")
                    raise
        else:
            response = self.getresponse()
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
                LOGGER.info(
                    "following redirect: link=%s",
                    response.headers.get("link")
                )
                null = response.read()
                redirect_path = self.parse_link_header(
                    response.headers.get("link")
                )
                self.path_stack.append(redirect_path)
                self.post(data=data)
            elif (
                HTTPStatus.BAD_REQUEST
                <= response.status <=
                HTTPStatus.INTERNAL_SERVER_ERROR
            ):
                # TODO: perform certain retries
                LOGGER.error(
                    "erroneous request: status=%i, reason=%s",
                    response.status, response.reason
                )
                return response
            elif HTTPStatus.INTERNAL_SERVER_ERROR <= response.status:
                # TODO: perform certain retries
                LOGGER.error(
                    "API issues: status=%i, reason=%s",
                    response.status, response.reason
                )
                return response

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
        self.base_path = path
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
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("delete")
        resp = self.post()
        LOGGER.info(
            "delete resource: status=%i, content=%s",
            resp_status,
            parameters["content"]
        )
        return resp.read()
        
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
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("export")
        resp = self.post()
        LOGGER.info(
            "delete resource: status=%i, content=%s",
            resp_status,
            parameters["content"]
        )
        return resp.read()

    def import_content(self, fp, **parameters):
        """Import content"""
        params = self.params
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            params += "&{}={}".format(key, value)
        self.path_stack.append(self.base_path + "?" + params)
        self.set_effective_headers("import")
        resp = self.post(fp)
        LOGGER.info(
            "delete resource: status=%i, content=%s",
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
