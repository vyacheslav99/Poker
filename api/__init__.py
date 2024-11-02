import logging
from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager

from configs import config
from .handlers.common import router as common_router
from . import db


@asynccontextmanager
async def db_setup(app: FastAPI):
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


def create_app() -> FastAPI:
    app = FastAPI(
        debug=config.DEBUG,
        title=config.SERVER_NAME,
        version=config.SERVER_VERSION,
        lifespan=db_setup
    )

    app.include_router(get_api_router())

    return app
