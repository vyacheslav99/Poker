import chardet
import mimetypes
import hashlib


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


# def handler(path: str, methods: List[str] | str, query_schema: Schema | None = None,
#             body_schema: Schema | None = None, response_schema: Schema | None = None):
#     def wrapper(func):
#         @wraps(func)
#         def wrapped(*args, **kwargs):
#             Router().register(
#                 routes=[path],
#                 methods=methods if isinstance(methods, (list, tuple)) else methods.split(','),
#                 func=func,
#                 class_name=None,
#                 attr_name=str(func),
#                 query_schema=query_schema,
#                 body_schema=body_schema,
#                 response_schema=response_schema
#             )
#         return wrapped
#
#     return wrapper

    # def _validate_request(self, query_schema: marshmallow.Schema | None = None, body_schema: marshmallow.Schema | None = None):
    #     if query_schema:
    #         self.request._params = query_schema().load(self.request.params)
    #     if body_schema:
    #         self.request._json = body_schema().load(self.request.json)
    #
    # def _validate_response(self, response, schema: marshmallow.Schema | None = None):
    #     if schema:
    #         response.body = schema().dump(response.body)

