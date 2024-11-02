import logging
from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager

from configs import config
from .handlers.common import router as common_router
from . import db


async def setup_db():
    logging.debug('startup db connections...')
    await db.setup(config.DB_CONNECTIONS)


async def db_shutdown():
    logging.debug('shutdown db connections...')
    await db.shutdown()

@asynccontextmanager
async def setup_infrastructure(app: FastAPI):
    await setup_db()
    # yield
    # await db_shutdown()


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
        lifespan=setup_infrastructure
    )
    app.include_router(get_api_router())

    return app


app = create_app()
