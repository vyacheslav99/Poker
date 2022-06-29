import chardet
import mimetypes

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_OCTET_STREAM = 'application/octet-stream'
CONTENT_TYPE_TEXT_PLAIN = 'text/plain'
CONTENT_TYPE_TEXT_HTML = 'text/html'


def get_content_type(file_name):
    return mimetypes.guess_type(file_name)[0] or CONTENT_TYPE_OCTET_STREAM


def decode(byte_str):
    enc = chardet.detect(byte_str)
    return byte_str.decode(enc['encoding'] or 'utf-8')
