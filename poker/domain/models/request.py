from enum import Enum


class HttpMethods(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    COPY = 'COPY'
    LINK = 'LINK'
    UNLINK = 'UNLINK'
    PURGE = 'PURGE'
    LOCK = 'LOCK'
    UNLOCK = 'UNLOCK'
    PROPFIND = 'PROPFIND'
    VIEW = 'VIEW'

    def __str__(self):
        return self.value