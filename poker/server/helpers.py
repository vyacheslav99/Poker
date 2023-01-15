import logging
import datetime
import json

from typing import Optional, Union, Any, Iterable, Mapping, Dict
from urllib import parse

from api.modules import utils


class HTTPException(Exception):

    def __init__(self, http_status: int, http_error: str, code: str = None, message: str = None):
        self.http_status: int = http_status
        self.http_error: str = http_error
        self.code = code
        self.message = message


class Request:

    def __init__(self, request_str: bytes):
        self._raw_request: bytes = request_str
        self._method: Optional[str] = None
        self._uri: Optional[str] = None
        self._protocol: Optional[str] = None
        self._params: Dict[str, Any] = {}
        self._headers: Dict[str, Any] = {}
        self._body: Optional[str] = None
        self._json: Any = None
        self._parse_request_str()

    def _parse_request_str(self):
        data = utils.decode(self._raw_request).split('\r\n')
        logging.debug(data[0])
        self._method, self._uri, self._protocol = data[0].split(' ')

        uri = self._uri.split('/')
        uri.pop(0)
        self._uri = '/{}'.format('/'.join(uri))
        if self._uri.find('?') > -1:
            self._uri, params = self._uri.split('?')

            params = params.split('&')
            for param in params:
                p, v = param.split('=', 1)
                self._params[p] = parse.unquote(v)

        self._uri = parse.unquote(self._uri)

        data.pop(0)
        while True:
            row = data.pop(0)
            if row == '':
                break

            p, v = row.split(':', 1)
            self._headers[p.strip()] = v.strip()

        self._body = '\r\n'.join(data)

        if self.is_json():
            self._json = json.loads(self._body)

    def is_json(self):
        return self._headers.get('Content-Type', '').lower() == utils.CONTENT_TYPE_JSON

    @property
    def method(self) -> Optional[str]:
        return self._method

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    @property
    def protocol(self) -> Optional[str]:
        return self._protocol

    @property
    def host(self) -> Optional[str]:
        return self._headers.get('Host', None)

    @property
    def params(self) -> Dict[str, Any]:
        return self._params

    @property
    def headers(self) -> Dict[str, Any]:
        return self._headers

    @property
    def body(self) -> Optional[str]:
        return self._body

    @property
    def json(self) -> Any:
        return self._json


class Response:

    def __init__(self, status: int, code: str, headers: Dict[str, Any] = None, body: Any = None, protocol: str = None):
        self._protocol: str = protocol or 'HTTP/1.1'
        self._status: int = status
        self._code: str = code
        self._headers: Dict[str, Any] = headers or self.default_headers()
        self.body: str = body or ''

    @classmethod
    def default_headers(cls, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        res = {
            'Content-Type': ('application/json', 'charset=utf-8'),
            'Content-Length': 0,
            'Date': datetime.datetime.today().strftime("%a, %d %b %Y %H:%M %Z"),
            'Server': 'Poker_Svc/1.0.0',
            # 'Content-Encoding': 'utf-8',
            'Connection': 'close'
        }

        res.update(headers or {})

        for h in res:
            if isinstance(res[h], tuple):
                res[h] = '; '.join(res[h])

        return res

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def status(self) -> int:
        return self._status

    @property
    def code(self) -> str:
        return self._code

    @property
    def headers(self) -> Dict[str, Any]:
        return self._headers

    @property
    def body(self) -> str:
        # return body str representation

        if isinstance(self._body, str):
            return self._body
        elif isinstance(self._body, bytes):
            return utils.decode(self._body)
        else:
            try:
                return json.dumps(self._body)
            except Exception:
                return str(self._body)

    @property
    def bytes(self) -> bytes:
        # return body bytes representation

        if isinstance(self._body, bytes):
            return self._body
        elif isinstance(self._body, str):
            return self._body.encode()
        else:
            try:
                return json.dumps(self._body).encode()
            except Exception:
                return str(self._body).encode()

    @protocol.setter
    def protocol(self, protocol: str):
        self._protocol = protocol

    @status.setter
    def status(self, status: int):
        self._status = status

    @code.setter
    def code(self, code: str):
        self._code = code

    @headers.setter
    def headers(self, headers: Union[Dict[str, Any], Iterable[Mapping[str, Any]]]):
        self._headers = dict(headers)

    def set_header(self, key: str, value: Any):
        self._headers[key] = value

    @body.setter
    def body(self, body: Any):
        self._body = body
        self.set_header('Content-Length', len(self.bytes) if body else 0)

    def __str__(self):
        data = ['{0} {1} {2}'.format(self._protocol, self._status, self._code)]
        data.extend('{0}: {1}'.format(*head) for head in self._headers.items())
        data.append('')
        if self._body is not None:
            data.append(self.body)

        return '\r\n'.join(data)

    def __bytes__(self):
        data = [('{0} {1} {2}'.format(self._protocol, self._status, self._code)).encode()]
        data.extend(('{0}: {1}'.format(*head)).encode() for head in self._headers.items())
        data.append(b'')
        if self._body is not None:
            data.append(self.bytes)

        return b'\r\n'.join(data)
