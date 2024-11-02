from fastapi import APIRouter

from .common import router as common_router


def get_api_router():
    router = APIRouter()
    router.include_router(common_router)
    # router.include_router(support_controller.router)
    return router
