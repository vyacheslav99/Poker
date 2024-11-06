from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api.models.security import User, Token, AuthData
from api.models.http import ContentType
from api.services.security import Security

router = APIRouter(prefix='/api', tags=['user'])


@router.get('/public-key')
def get_public_key():
    return Response(Security.get_public_key(), media_type=ContentType.CONTENT_TYPE_PEM)


@router.post('/login')
async def authorize(body: AuthData, request: Request) -> Token:
    return await Security().do_authorize_safe(body.username, body.password, request=request)


@router.post('/login-form')
async def login_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request) -> Token:
    return await Security().do_authorize_unsafe(form_data.username, form_data.password, request=request)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(body: AuthData) -> User:
    return await Security().create_user(body)


@router.get('/me', response_model=User)
async def get_current_user(curr_user: User = Depends(Security.check_auth)):
    return curr_user
