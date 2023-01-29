from typing import List
from functools import wraps

from server.helpers import Request, Response
from server.router import Router
from domain.models.base_model import BaseModel

router = Router()


def route(rule: str, methods: List[str], query_schema=None, body_schema=None, response_schema=None):
    def prepare_body(body):
        if isinstance(body, BaseModel):
            body = body.as_dict()

        return dict(success=True, result=response_schema().dump(body) if response_schema else body)

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
                        response.body = prepare_body(response.body)
                elif isinstance(response, tuple):
                    if response[-1] < 400:
                        response = (prepare_body(response[0]), *response[1:])
                else:
                    response = prepare_body(response)

            return response

        return wrapped

    return wrapper
