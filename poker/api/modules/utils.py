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