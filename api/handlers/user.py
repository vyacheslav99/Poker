import uuid

from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from api.handlers import CheckAuthProvider
from api.models.user import UserPublic, Session, Token, LoginBody, ChangePasswordBody, ChangeUsernameBody, UserPatchBody
from api.models.http import ContentType
from api.models.common import SuccessResponse, DeletedResponse
from api.services.user import UserService

router = APIRouter(prefix='/api', tags=['user'])


@router.get('/public-key', response_model=str)
def get_public_key():
    return Response(UserService.get_public_key(), media_type=ContentType.CONTENT_TYPE_PEM)


@router.post('/login')
async def authorize(body: LoginBody, request: Request) -> Token:
    return await UserService().do_authorize_safe(body.username, body.password, request=request)


@router.post('/login-form')
async def login_by_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request) -> Token:
    return await UserService().do_authorize_unsafe(form_data.username, form_data.password, request=request)


@router.post('/logout', response_model=SuccessResponse)
async def logout(curr_user: CheckAuthProvider):
    await UserService().do_logout(curr_user)
    return SuccessResponse()


@router.post('/user', status_code=status.HTTP_201_CREATED)
async def signup(body: LoginBody) -> UserPublic:
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


@router.get('/user/sessions')
async def get_sessions(curr_user: CheckAuthProvider) -> list[Session]:
    return await UserService().get_sessions(curr_user)


@router.delete('/user/sessions', response_model=DeletedResponse)
async def close_another_sessions(curr_user: CheckAuthProvider):
    return DeletedResponse(deleted=await UserService().close_another_sessions(curr_user))


@router.delete('/user/sessions/{session_id}', response_model=DeletedResponse)
async def close_session(session_id: uuid.UUID, curr_user: CheckAuthProvider):
    await UserService().close_session(curr_user, session_id)
    return DeletedResponse(deleted=1)
