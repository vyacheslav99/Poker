import jwt
import logging
import base64
import rsa
import uuid

from datetime import timedelta, datetime, timezone
from typing import Annotated

from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from api import config
from api.models.user import UserDTO, Token, AuthData
from api.repositories.user import UserRepo


class UserService:

    def __init__(self):
        self._pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @staticmethod
    async def get_user_by_token(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl='/api/user/login-form'))
    ) -> UserDTO:
        unauthorized_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization token invalid',
            headers={'WWW-Authenticate': 'Bearer'}
        )

        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            username = payload.get('sub')
            expires_in = payload.get('exp')

            if username is None:
                raise unauthorized_exception

            user = await UserRepo.get_user(username=username)

            if not user or user.disabled:
                raise unauthorized_exception

            if expires_in and datetime.now(tz=timezone.utc) > datetime.fromtimestamp(expires_in, tz=timezone.utc):
                raise unauthorized_exception

            return user
        except InvalidTokenError as e:
            logging.error('Cannot decode token!', exc_info=e)
            raise unauthorized_exception

    def decrypt_password(self, password_b64: str) -> str:
        private_key = rsa.PrivateKey.load_pkcs1(config.RSA_PRIVATE_KEY.encode())
        encrypted_pwd = base64.urlsafe_b64decode(password_b64.encode())
        decrypted_pwd = rsa.decrypt(encrypted_pwd, private_key).decode()
        return decrypted_pwd

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + (
            expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({'exp': expire})

        return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    async def do_authorize(self, username: str, password_b64: str) -> Token:
        decrypted_pwd = self.decrypt_password(password_b64)
        user = await UserRepo.get_user(username=username)

        if not user or user.disabled or not self._pwd_context.verify(decrypted_pwd, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'}
            )

        token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = self.create_access_token(data={'sub': user.username}, expires_delta=token_expires)

        return Token(access_token=token, token_type='bearer')

    async def create_user(self, user: AuthData) -> UserDTO:
        return await UserRepo.create_user(UserDTO(
            uid=uuid.uuid4(),
            username=user.username,
            password=self._pwd_context.hash(self.decrypt_password(user.password)),
            fullname=user.username
        ))