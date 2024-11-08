from enum import StrEnum


class ContentType(StrEnum):
    CONTENT_TYPE_JSON = 'application/json'
    CONTENT_TYPE_OCTET_STREAM = 'application/octet-stream'
    CONTENT_TYPE_TEXT_PLAIN = 'text/plain'
    CONTENT_TYPE_TEXT_HTML = 'text/html'
    CONTENT_TYPE_PEM = 'application/x-pem-file'


AVAILABLE_IMAGE_TYPES = {'.bmp', '.jpg', '.jpeg', '.png', '.ico'}
