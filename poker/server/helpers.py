import logging
import datetime
import json

from urllib import parse
from . import utils


class HTTPException(Exception):

    def __init__(self, http_code, http_status, code, message):
        self.http_status = http_status
        self.http_code = http_code
        self.code = code
        self.message = message


class Request(object):

    def __init__(self, request_str):
        self._raw_request = request_str
        self._method = None
        self._uri = None
        self._protocol = None
        self._params = {}
        self._headers = {}
        self._body = None
        self._json = None
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
        return self._headers.get('Content-Type', '').lower() == 'application/json'

    @property
    def method(self):
        return self._method

    @property
    def uri(self):
        return self._uri

    @property
    def protocol(self):
        return self._protocol

    @property
    def host(self):
        return self._headers.get('Host', None)

    @property
    def params(self):
        return self._params

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body

    @property
    def json(self):
        return self._json


class Response(object):

    def __init__(self, code, status, protocol=None, headers=None, body=None):
        self._protocol = protocol or 'HTTP/1.1'
        self._code = code
        self._status = status
        self._headers = headers or self.default_headers()
        self.body = body or ''

    @classmethod
    def default_headers(cls, headers=None):
        res = {
            'Date': datetime.datetime.today().strftime("%a, %d %b %Y %H:%M %Z"),
            'Server': 'Poker_Svc/1.0.0',
            'Content-Length': 0,
            'Content-Type': 'application/json',
            'Content-Encoding': 'utf-8',
            'Connection': 'close'
        }

        res.update(headers or {})
        return res

    @property
    def protocol(self):
        return self._protocol

    @property
    def code(self):
        return self._code

    @property
    def status(self):
        return self._status

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        # return str representation

        if isinstance(self._body, str):
            return self._body
        elif isinstance(self._body, bytes):
            return utils.decode(self._body)
        else:
            return str(self._body)

    @property
    def bytes(self):
        # return bytes representation

        if isinstance(self._body, bytes):
            return self._body
        elif isinstance(self._body, str):
            return self._body.encode()
        else:
            return str(self._body).encode()

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = protocol

    @code.setter
    def code(self, code):
        self._code = code

    @status.setter
    def status(self, status):
        self._status = status

    @headers.setter
    def headers(self, headers):
        self._headers = dict(headers)

    def set_header(self, key, value):
        self._headers[key] = value

    @body.setter
    def body(self, body):
        self._body = body
        self.set_header('Content-Length', len(self.bytes) if body else 0)

    def __str__(self):
        data = ['{0} {1} {2}'.format(self._protocol, self._code, self._status)]
        data.extend('{0}: {1}'.format(*head) for head in self._headers.items())
        data.append('')
        if self._body is not None:
            data.append(self.body)

        return '\r\n'.join(data)

    def __bytes__(self):
        data = [('{0} {1} {2}'.format(self._protocol, self._code, self._status)).encode()]
        data.extend(('{0}: {1}'.format(*head)).encode() for head in self._headers.items())
        data.append(b'')
        if self._body is not None:
            data.append(self.bytes)

        return b'\r\n'.join(data)
