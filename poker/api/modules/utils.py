import chardet
import mimetypes
import hashlib

from functools import wraps

from server.helpers import Request, Response

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_OCTET_STREAM = 'application/octet-stream'
CONTENT_TYPE_TEXT_PLAIN = 'text/plain'
CONTENT_TYPE_TEXT_HTML = 'text/html'


def get_content_type(file_name: str) -> str:
    return mimetypes.guess_type(file_name)[0] or CONTENT_TYPE_OCTET_STREAM


def decode(byte_str: bytes) -> str:
    enc = chardet.detect(byte_str)
    return byte_str.decode(enc['encoding'] or 'utf-8')


def encrypt(value: str) -> str:
    return hashlib.sha224(value.encode()).hexdigest()


def schemas_definition(query_schema=None, body_schema=None, response_schema=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            request: Request = args[0]

            if query_schema:
                request._params = query_schema().load(request.params)
            if body_schema:
                request._json = body_schema().load(request.json)

            response = func(*args, **kwargs)

            if response_schema:
                if isinstance(response, Response):
                    if response.status < 400:
                        response.body = response_schema().dump(response.body)
                elif isinstance(response, tuple):
                    if response[-1] < 400:
                        response = (response_schema().dump(response[0]), *response[1:])
                else:
                    response = response_schema().dump(response)

            return response

        return wrapped

    return wrapper
