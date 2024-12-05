from typing import Any
from fastapi import HTTPException, status


class BadRequestError(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Bad request'

    def __init__(self, status_code: int = None, detail: Any = None):
        self.status_code = status_code or self.status_code
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail)


class UnauthorizedError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Unauthorized'
    headers = {'WWW-Authenticate': 'Bearer'}

    def __init__(self, detail: Any = None):
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail, headers=self.headers)


class ForbiddenError(BadRequestError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Access denied'

    def __init__(self, detail: Any = None):
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail)


class NotFoundError(BadRequestError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Not found'

    def __init__(self, detail: Any = None):
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail)


class ConflictError(BadRequestError):
    status_code = status.HTTP_409_CONFLICT
    detail = 'Conflict'

    def __init__(self, detail: Any = None):
        self.detail = detail or self.detail
        super().__init__(self.status_code, detail=self.detail)


class NoChangesError(Exception):
    pass
