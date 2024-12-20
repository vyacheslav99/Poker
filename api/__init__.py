import os
import logging

from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.middleware.errors import ServerErrorMiddleware

from api import db, config
from .handlers import base_router, v1_router


@asynccontextmanager
async def setup_infrastructure(app: FastAPI):
    """
    Замена deprecated механизму событий FastAPI "startup", "shutdown".
    Передаем этот метод в качестве параметра lifespan конструктору FastAPI:
    `app = FastAPI(..., lifespan=setup_infrastructure)`
    Все что до строки yield выполняется при старте сервиса, что после - выполняется при остановке
    """

    logging.debug('startup db connections...')
    await db.setup(config.DB_CONNECTIONS)

    yield

    logging.debug('shutdown db connections...')
    await db.shutdown()


def get_api_routers() -> APIRouter:
    router = APIRouter()
    router.include_router(base_router)
    router.include_router(v1_router, prefix='/api')
    return router


async def handle_error(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, HTTPException):
        status_code = getattr(exc, 'status_code', getattr(exc, 'code', status.HTTP_500_INTERNAL_SERVER_ERROR))

        if not isinstance(status_code, int):
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if config.DEBUG:
            message = getattr(exc, 'message', str(exc))
        else:
            message = 'Oops, something went wrong'

        exc = HTTPException(status_code=status_code, detail=message)

    return await http_exception_handler(request, exc)


def create_app() -> FastAPI:
    if not os.path.exists(config.FILESTORE_DIR):
        os.makedirs(config.FILESTORE_DIR, exist_ok=True)
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR, exist_ok=True)
    if not os.path.exists(config.LOGS_DIR):
        os.makedirs(config.LOGS_DIR, exist_ok=True)

    app = FastAPI(
        debug=config.DEBUG,
        title=config.SERVER_NAME,
        version=config.SERVER_VERSION,
        lifespan=setup_infrastructure
    )

    app.add_middleware(ServerErrorMiddleware, handler=handle_error)
    app.include_router(get_api_routers())
    app.mount('/static/files', StaticFiles(directory=config.FILESTORE_DIR), name='static')

    return app
