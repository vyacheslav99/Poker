from typing import Annotated
from fastapi import APIRouter, status, UploadFile, Query

from api.handlers import RequiredAuthProvider, OptionalAuthProvider
from api.models.user import (UserPublic, ChangePasswordBody, ChangeUsernameBody, UserPatchBody, DeleteUserBody,
                             ClientParams, GameOptions, OverallStatisticsResponse, StatisticsSortFields)
from api.models.security import Token, LoginBody
from api.models.common import SuccessResponse
from api.services.user import UserService

router = APIRouter(prefix='/api', tags=['user'])


@router.post('/user', status_code=status.HTTP_201_CREATED)
async def create_user(body: LoginBody) -> UserPublic:
    return await UserService().create_user(body)


@router.get('/user', response_model=UserPublic)
async def get_current_user(curr_user: RequiredAuthProvider):
    return curr_user


@router.patch('/user', response_model=UserPublic)
async def change_user(body: UserPatchBody, curr_user: RequiredAuthProvider):
    return await UserService().change_user(curr_user, body)


@router.put('/user/avatar', response_model=UserPublic)
async def change_avatar(file: UploadFile, curr_user: RequiredAuthProvider):
    return await UserService().change_avatar(curr_user, file)


@router.delete('/user/avatar', response_model=UserPublic)
async def clear_avatar(curr_user: RequiredAuthProvider):
    return await UserService().clear_avatar(curr_user)


@router.patch('/user/passwd', response_model=SuccessResponse)
async def change_password(body: ChangePasswordBody, curr_user: RequiredAuthProvider):
    await UserService().change_password(curr_user, body.password, body.new_password, close_sessions=body.close_sessions)
    return SuccessResponse()


@router.patch('/user/username', response_model=Token)
async def change_username(body: ChangeUsernameBody, curr_user: RequiredAuthProvider):
    return await UserService().change_username(curr_user, body.new_username)


@router.delete('/user', response_model=SuccessResponse)
async def delete_user(body: DeleteUserBody, curr_user: RequiredAuthProvider):
    await UserService().delete_user(curr_user, body.password)
    return SuccessResponse()


@router.get('/user/params', response_model=ClientParams)
async def get_user_params(curr_user: RequiredAuthProvider):
    return await UserService().get_user_params(curr_user)


@router.get('/user/game_options', response_model=GameOptions)
async def get_user_game_options(curr_user: RequiredAuthProvider):
    return await UserService().get_user_game_options(curr_user)


@router.put('/user/params', response_model=SuccessResponse)
async def set_user_params(body: ClientParams, curr_user: RequiredAuthProvider):
    await UserService().set_user_params(curr_user, body)
    return SuccessResponse()


@router.put('/user/game_options', response_model=SuccessResponse)
async def set_user_game_options(body: GameOptions, curr_user: RequiredAuthProvider):
    await UserService().set_user_game_options(curr_user, body)
    return SuccessResponse()


@router.get('/is_free_username', response_model=SuccessResponse)
async def username_is_free(username: str):
    is_free = await UserService().username_is_free(username)
    return SuccessResponse(success=is_free)


@router.get('/statistics', response_model=OverallStatisticsResponse)
async def get_overall_statistics(
    curr_user: OptionalAuthProvider, include_user_ids: Annotated[list[str] | None, Query()] = None,
    sort_field: StatisticsSortFields = None, sort_desc: bool = None, limit: int = None
):
    data = await UserService().get_statistics(
        curr_user, include_user_ids=include_user_ids, sort_field=sort_field, sord_desc=sort_desc, limit=limit
    )

    return OverallStatisticsResponse(items=data, total=len(data))


@router.delete('/user/statistics', response_model=SuccessResponse)
async def reset_user_statistics(curr_user: RequiredAuthProvider):
    await UserService().reset_user_statistics(curr_user)
    return SuccessResponse()
