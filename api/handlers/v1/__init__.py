from fastapi import APIRouter

from .security import router as sec_router
from .user import router as user_router
from .misc import router as misc_router
from .game import router as game_router


v1_router = APIRouter(prefix='/v1')
v1_router.include_router(sec_router)
v1_router.include_router(user_router)
v1_router.include_router(misc_router)
v1_router.include_router(game_router)
