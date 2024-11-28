import uuid

from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from api.handlers import RequiredAuthProvider
from api.models.security import Session, Token, LoginBody
from api.models.http import ContentType
from api.models.common import SuccessResponse, DeletedResponse, error_responses
from api.services.security import Security

router = APIRouter(prefix='/api', tags=['security'])


@router.get(
    path='/public-key',
    response_model=str,
    summary='Публичный ключ шифрования',
    description='Получить публичный ключ сервера для шифрования им данных на клиенте, которые надо отправлять на '
                'сервер в зашифрованном виде',
    response_description='Публичный ключ, тип ответа: `application/x-pem-file`',
    responses=error_responses()
)
def get_public_key():
    return Response(Security.get_public_key(), media_type=ContentType.CONTENT_TYPE_PEM)


@router.post(
    path='/login',
    response_model=Token,
    summary='Авторизация (безопасная)',
    description='Авторизация пользователя защищенная шифрованием. Пароль принимает в зашифрованном виде. '
                'Шифрование публичным ключем, выдаваемым сервером по ручке `get /public-key`',
    responses=error_responses()
)
async def authorize(request: Request, body: LoginBody):
    return await Security().do_authorize_safe(body.username, body.password, request=request)


@router.post(
    path='/login-form',
    response_model=Token,
    summary='Авторизация (открытая)',
    description='Авторизация пользователя с передачей пароля в открытом виде',
    responses=error_responses()
)
async def login_by_form(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await Security().do_authorize_unsafe(form_data.username, form_data.password, request=request)


@router.post(
    path='/logout',
    response_model=SuccessResponse,
    summary='Разлогиниться',
    description='Разлогиниться и удалить текущий сеанс с сервера',
    responses=error_responses()
)
async def logout(user: RequiredAuthProvider):
    await Security().do_logout(user)
    return SuccessResponse()


@router.get(
    path='/user/sessions',
    response_model=list[Session],
    summary='Активные сеансы пользователя',
    description='Список активных сеансов текущего пользователя',
    responses=error_responses()
)
async def get_sessions(user: RequiredAuthProvider):
    return await Security().get_sessions(user)


@router.delete(
    path='/user/sessions',
    response_model=DeletedResponse,
    summary='Завершить другие сеансы пользователя',
    description='Завершить все прочие сеансы пользователя, кроме текущего - т.е. разлогинить все остальные сеансы',
    responses=error_responses()
)
async def close_another_sessions(user: RequiredAuthProvider):
    return DeletedResponse(deleted=await Security().close_another_sessions(user))


@router.delete(
    path='/user/sessions/{session_id}',
    response_model=DeletedResponse,
    summary='Завершить конкретный сеанс',
    responses=error_responses()
)
async def close_session(user: RequiredAuthProvider, session_id: uuid.UUID):
    await Security().close_session(user, session_id)
    return DeletedResponse(deleted=1)
