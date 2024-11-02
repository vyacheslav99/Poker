from fastapi import APIRouter, FastAPI

from configs import config
from .handlers.common import router as common_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(common_router)
    # router.include_router(support_controller.router)
    return router


def create_app() -> FastAPI:
    app = FastAPI(debug=config.DEBUG, title=config.SERVER_NAME, version=config.SERVER_VERSION)
    app.include_router(get_api_router())
    return app


app = create_app()
