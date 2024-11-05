from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.models.user import User, Token, AuthData
from api.services.user import UserService

router = APIRouter(prefix='/api/user', tags=['user'])


@router.get('/me', response_model=User)
async def get_current_user(curr_user: User = Depends(UserService.get_user_by_token)):
    return curr_user


@router.post('/auth')
async def authorize(body: AuthData) -> Token:
    return await UserService().do_authorize(body.username, body.password)


@router.post('/login-form')
async def login_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await UserService().do_authorize(form_data.username, form_data.password)


@router.post('/register')
async def register(body: AuthData) -> User:
    return await UserService().create_user(body)
