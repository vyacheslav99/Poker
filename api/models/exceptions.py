from typing import Any
from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Unauthorized'
    headers = {'WWW-Authenticate': 'Bearer'}

    def __init__(self, detail: Any = None):
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail, headers=self.headers)
