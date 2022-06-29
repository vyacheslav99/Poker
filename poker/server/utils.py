import chardet
import mimetypes

CONTENT_TYPE_JSON = 'application/json'


def get_content_type(file_name):
    return mimetypes.guess_type(file_name)[0] or 'application/octet-stream'


def decode(byte_str):
    enc = chardet.detect(byte_str)
    return byte_str.decode(enc['encoding'] or 'utf-8')
