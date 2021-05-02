"""Connector objects"""
from http import client, HTTPStatus
from io import IOBase
from logging import getLogger
from urllib.parse import urlencode


LOGGER = getLogger(__name__)


PARAMETERS = [
    "action", "allRecords", "arm", "arms", "compactDisplay",
    "content", "csvDelimiter", "data", "dateFormat",
    "dateRangeBegin", "dateRangeEnd", "decimalCharacter", "event",
    "events", "exportCheckboxLabel", "exportDataAccessGroups",
    "exportFiles", "exportSurveyFields", "field", "fields", "file",
    "filterLogic", "forceAutoNumber", "format", "forms",
    "instrument", "override", "overwriteBehavior", "rawOrLabel",
    "rawOrLabelHeaders", "record", "records", "repeat_instance",
    "report_id", "returnContent", "returnFormat",
    "returnMetadataOnly", "token", "type",
]


class BaseConnector(client.HTTPSConnection):
    """HTTP methods container"""

    path_stack = []
    static_headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }

    def __enter__(self):
        """Enter context"""
        if self.sock is None:
            self.connect()
        return self

    def __exit__(self, typ, val, trb):
        """Exit context"""
        self.close()
    
    def post(self, body):
        """Handle HTTP POST procedure"""
        try:
            self.putrequest(
                method="POST", url=self.path_stack[-1]
            )
            for k,v in self.static_headers.items():
                self.putheader(k,v)
            self.putheader("content-length", len(body))
            self.endheaders(message_body=body)
        except Exception as e:
            LOGGER.exception("request threw exception: exc=%s", e)
            if isinstance(e, client.NotConnected):
                try:
                    LOGGER.info("trying to reconnect")
                    self.connect()
                    self.post(body=body)
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
                self.post(body=body)
            elif response.status >= HTTPStatus.BAD_REQUEST:
                # 400s and 500s compacted into one elif for now
                # TODO: perform certain retries
                # TODO: verify REDCap exceptions are tied to 400s/500s
                LOGGER.error(
                    "erroneous request: status=%i, reason=%s",
                    response.status, response.reason
                )
                return response
            

class Connector(BaseConnector):
    """WIP REDCap methods container"""

    def __init__(self, host, path, token, **kwargs):
        """Construct interface"""
        super().__init__(host)
        if path is None or token is None:
            raise RuntimeError("path and/or token required")
        self.path_stack.append(path)
        self._parameters = {
            "token": token, "format": kwargs.pop("format", "json")
        }
        for k,v in kwargs.items():
            if k in PARAMETERS:
                self._parameters[k] = v

    def url_encode(self, **parameters):
        """Return url-encoded body bytes"""
        body = self._parameters
        for key, value in parameters.items():
            if key not in PARAMETERS:
                raise Exception("bad API parameter")
            body[key] = value
        return urlencode(body).encode("latin-1")

    def delete_content(self, content, **parameters):
        """Delete content"""
        if "data" in parameters:
            raise Exception("Can't delete with data")
        body = self.url_encode(
            action="delete", content=content, **parameters
        )
        resp = self.post(body)
        LOGGER.info(
            "delete resource: status=%i, content=%s",
            resp.status,
            content
        )
        return resp.read()
        
    def export_content(self, content, **parameters):
        """Export content"""
        if "data" in parameters:
            raise Exception("Can't export with data")
        body = self.url_encode(
            action="export", content=content, **parameters
        )
        resp = self.post(body)
        LOGGER.info(
            "export resource: status=%i, content=%s",
            resp.status,
            content
        )
        return resp.read()

    def import_content(self, content, data, **parameters):
        """Import content"""
        # TODO: Check if format param agrees w actual data
        body = self.url_encode(
            action="import", content=content, **parameters
        )
        resp = self.post(body)
        LOGGER.info(
            "import resource: status=%i, content=%s",
            resp.status,
            content
        )
        return resp.read()
        
    def arms(self, action, **parameters):
        """Modify arms"""
        return getattr(self, "{}_content".format(action))(
            content="arm", **parameters
        )

    def events(self, action, **parameters):
        """Modify events"""
        return getattr(self, "{}_content".format(action))(
            content="event", **parameters
        )

    def field_names(self, action, **parameters):
        """Modify field_names"""
        return getattr(self, "{}_content".format(action))(
            content="exportFieldNames", **parameters
        )

    def files(self, action, **parameters):
        """Modify files"""
        return getattr(self, "{}_content".format(action))(
            content="file", **parameters
        )

    def instruments(self, action, **parameters):
        """Modify instruments"""
        return getattr(self, "{}_content".format(action))(
            content="instrument", **parameters
        )

    def metadata(self, action, **parameters):
        """Modify metadata"""
        return getattr(self, "{}_content".format(action))(
            content="metadata", **parameters
        )

    def projects(self, action, **parameters):
        """Modify projects"""
        return getattr(self, "{}_content".format(action))(
            content="projects", **parameters
        )

    def records(self, action, **parameters):
        """Modify records"""
        return getattr(self, "{}_content".format(action))(
            content="records", **parameters
        )
        
    def repeating_ie(self, action, **parameters):
        """Modify repeating_ie"""
        return getattr(self, "{}_content".format(action))(
            content="repeating_ie", **parameters
        )

    def reports(self, action, **parameters):
        """Modify reports"""
        return getattr(self, "{}_content".format(action))(
            content="reports", **parameters
        )

    def redcap(self, action, **parameters):
        """Modify redcap"""
        return getattr(self, "{}_content".format(action))(
            content="redcap", **parameters
        )

    def surveys(self, action, **parameters):
        """Modify surveys"""
        return getattr(self, "{}_content".format(action))(
            content="surveys", **parameters
        )

    def users(self, action, **parameters):
        """Modify users"""
        return getattr(self, "{}_content".format(action))(
            content="users", **parameters
        )


__all__ = ["Connector",]
