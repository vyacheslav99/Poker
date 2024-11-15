from fastapi import APIRouter, status, UploadFile

from api.handlers import CheckAuthProvider
from api.models.user import (UserPublic, ChangePasswordBody, ChangeUsernameBody, UserPatchBody, DeleteUserBody,
                             ClientParams, GameOptions)
from api.models.security import Token, LoginBody
from api.models.common import SuccessResponse
from api.services.user import UserService

router = APIRouter(prefix='/api', tags=['user'])


@router.post('/user', status_code=status.HTTP_201_CREATED)
async def create_user(body: LoginBody) -> UserPublic:
    return await UserService().create_user(body)


@router.get('/user', response_model=UserPublic)
async def get_current_user(curr_user: CheckAuthProvider):
    return curr_user


@router.patch('/user', response_model=UserPublic)
async def change_user(body: UserPatchBody, curr_user: CheckAuthProvider):
    return await UserService().change_user(curr_user, body)


@router.put('/user/avatar', response_model=UserPublic)
async def change_avatar(file: UploadFile, curr_user: CheckAuthProvider):
    return await UserService().change_avatar(curr_user, file)


@router.delete('/user/avatar', response_model=UserPublic)
async def clear_avatar(curr_user: CheckAuthProvider):
    return await UserService().clear_avatar(curr_user)


@router.patch('/user/passwd', response_model=SuccessResponse)
async def change_password(body: ChangePasswordBody, curr_user: CheckAuthProvider):
    await UserService().change_password(curr_user, body.password, body.new_password, close_sessions=body.close_sessions)
    return SuccessResponse()


@router.patch('/user/username', response_model=Token)
async def change_username(body: ChangeUsernameBody, curr_user: CheckAuthProvider):
    return await UserService().change_username(curr_user, body.new_username)


@router.delete('/user', response_model=SuccessResponse)
async def delete_user(body: DeleteUserBody, curr_user: CheckAuthProvider):
    await UserService().delete_user(curr_user, body.password)
    return SuccessResponse()


@router.get('/user/params', response_model=ClientParams)
async def get_user_params(curr_user: CheckAuthProvider):
    return await UserService().get_user_params(curr_user)


@router.get('/user/game_options', response_model=GameOptions)
async def get_user_game_options(curr_user: CheckAuthProvider):
    return await UserService().get_user_game_options(curr_user)


@router.put('/user/params', response_model=SuccessResponse)
async def set_user_params(body: ClientParams, curr_user: CheckAuthProvider):
    await UserService().set_user_params(curr_user, body)
    return SuccessResponse()


@router.put('/user/game_options', response_model=SuccessResponse)
async def set_user_game_options(body: GameOptions, curr_user: CheckAuthProvider):
    await UserService().set_user_game_options(curr_user, body)
    return SuccessResponse()


@router.get('/is_free_username', response_model=SuccessResponse)
async def username_is_free(username: str):
    is_free = await UserService().username_is_free(username)
    return SuccessResponse(success=is_free)
