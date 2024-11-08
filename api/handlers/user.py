from fastapi import APIRouter

from api.models.security import UserPublic
from api.models.user import UserPatchBody
from api.handlers import CheckAuthProvider
from api.services.user import UserService

router = APIRouter(prefix='/api', tags=['user'])


@router.patch('/user', response_model=UserPublic)
async def change_user(body: UserPatchBody, curr_user: CheckAuthProvider):
    return await UserService().change_user(curr_user, body)
