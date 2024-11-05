import logging
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler
from starlette.middleware.errors import ServerErrorMiddleware
from contextlib import asynccontextmanager

from api import db, config
from .handlers.common import router as common_router


@asynccontextmanager
async def db_setup(app: FastAPI):
    """
    Замена deprecated механизму событий FastAPI "startup", "shutdown".
    Передаем этот метод в качестве параметра lifespan конструктору FastAPI:
    >>> app = FastAPI(..., lifespan=db_setup)
    Все что до строки yield выполняется при старте сервиса, что после - выполняется при остановке
    """

    logging.debug('startup db connections...')
    await db.setup(config.DB_CONNECTIONS)

    yield

    logging.debug('shutdown db connections...')
    await db.shutdown()


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(common_router)
    # router.include_router(support_controller.router)
    return router


async def handle_error(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, HTTPException):
        status_code = getattr(exc, 'status_code', getattr(exc, 'code', 500))
        message = getattr(exc, 'message', str(exc))
        exc = HTTPException(status_code=status_code, detail=message)

    return await http_exception_handler(request, exc)


def create_app() -> FastAPI:
    app = FastAPI(
        debug=config.DEBUG,
        title=config.SERVER_NAME,
        version=config.SERVER_VERSION,
        lifespan=db_setup
    )

    app.add_middleware(ServerErrorMiddleware, handler=handle_error)
    app.include_router(get_api_router())

    return app
