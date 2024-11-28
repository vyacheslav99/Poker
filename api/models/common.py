from typing import Any
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True


class DeletedResponse(SuccessResponse):
    deleted: int


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any] | list[str | dict[str, Any]]


def error_responses() -> dict:
    return {
        '4XX': {
            'model': ErrorResponse,
            'description': 'Bad request (client error)'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error'
        }
    }
