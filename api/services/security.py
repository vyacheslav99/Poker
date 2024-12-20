import jwt
import logging
import base64
import rsa

from uuid import UUID, uuid4
from datetime import timedelta, datetime, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
from passlib.context import CryptContext
from pydantic import ValidationError
from binascii import Error as Base64DecodeError

from api import config
from api.models.user import User
from api.models.security import  Token, TokenPayload, Session
from api.models.exceptions import BadRequestError, UnauthorizedError, NotFoundError, ForbiddenError
from api.repositories.user import UserRepo


class Security:

    def __init__(self):
        self._pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def calc_hash(self, value: str) -> str:
        return self._pwd_context.hash(value)

    def verify_hash(self, value: str, hashed: str) -> bool:
        return self._pwd_context.verify(value, hashed)

    def decrypt_password(self, password_b64: str) -> str:
        """
        Расшифровывает пароль, зашифрованный публичным ключем сервиса.
        Пароль приходит закодированным в base64, предварительно раскодирует его.
        """

        private_key = rsa.PrivateKey.load_pkcs1(config.RSA_PRIVATE_KEY.encode())

        try:
            encrypted_pwd = base64.urlsafe_b64decode(password_b64.encode())
            decrypted_pwd = rsa.decrypt(encrypted_pwd, private_key).decode()
        except Base64DecodeError as e:
            logging.error('Decryption error: incorrect base64 string', exc_info=e)
            raise RequestValidationError([{'password': 'Unsupported data type. Data is not a base64 encoded string'}])
        except rsa.DecryptionError as e:
            logging.error('Decryption error: encrypted with the wrong public key', exc_info=e)
            raise RequestValidationError([{'password': 'Wrong encryptrd data'}])

        return decrypted_pwd

    def create_access_token(self, username: str, session_id: UUID, expires_delta: timedelta = None) -> str:
        """
        Создает Bearer токен для авторизации по нему на стороне клиента (клиент будет передавать его в хедере
        Authorization авторизованных запросов)

        Возвращает зашифрованный с помощью jwt токен
        """

        payload = TokenPayload(
            sid=str(session_id),
            sub=username,
            exp=int((
                datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
            ).timestamp())
        )

        return jwt.encode(payload.model_dump(), config.SECRET_KEY, algorithm=config.ALGORITHM)

    @staticmethod
    def get_public_key() -> str:
        """
        Получить публичный ключ для шифрования данных на стороне клиента, которые небезопасно передавать в открытом виде
        (например пароли при авторизации и регистрации)
        """

        if config.RSA_PUBLIC_KEY:
            return config.RSA_PUBLIC_KEY

        raise NotFoundError(detail='No public keys found')

    @staticmethod
    async def get_auth(token: str = Depends(OAuth2PasswordBearer(tokenUrl='/api/v1/login-form'))) -> User:
        """
        Проверка авторизации по Bearer токену из заголовка Authorization. Авторизация обязательна

        Токен из заголовка извлекает класс OAuth2PasswordBearer и передает его в параметре token в метод.
        Если токен есть - проверит валидность и вернет объект пользователя.
        Если токена нет - возникнет ошибка авторизации.
        """

        return await Security.check_auth(token)

    @staticmethod
    async def get_auth_optional(
        token: str | None = Depends(OAuth2PasswordBearer(tokenUrl='/api/v1/login-form', auto_error=False))
    ) -> User | None:
        """
        Проверка авторизации по Bearer токену из заголовка Authorization. Авторизация не обязательна

        Токен из заголовка извлекает класс OAuth2PasswordBearer и передает его в параметре token в метод.
        Если токен есть - проверит валидность и вернет объект пользователя.
        Если токена нет - вернет None.
        """

        if not token:
            return None

        return await Security.check_auth(token)

    @staticmethod
    async def check_auth(token: str) -> User:
        """
        Проверка авторизации по Bearer токену из заголовка Authorization.

        Токен - это зашифрованный jwt json-объект представление модели TokenPayload.
        Метод расшифровывает токен, выполняет все проверки его валидности, валидности сессии и пользователя,
        после чего возвращает данные пользователя из БД.
        """

        try:
            payload = TokenPayload(**jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM]))
            session = await UserRepo.get_session(UUID(payload.sid))
            user = await UserRepo.get_user(username=payload.sub)

            if not session:
                raise UnauthorizedError(detail='Session is closed')

            if not user or session.uid != user.uid:
                raise UnauthorizedError(detail='Invalid token')

            if user.disabled or user.is_robot:
                raise UnauthorizedError(detail='User is blocked')

            if datetime.now(tz=timezone.utc) > datetime.fromtimestamp(payload.exp, tz=timezone.utc):
                await UserRepo.delete_sessions([session.sid])
                raise UnauthorizedError(detail='Session has been expired')

            user.curr_sid = session.sid
            return user
        except (InvalidTokenError, ValidationError) as e:
            logging.error('Cannot decode token!', exc_info=e)
            raise UnauthorizedError(detail='Invalid token')

    async def do_authorize_safe(self, username: str, passwd_encrypted: str, request: Request = None) -> Token:
        """
        Безопасная авторизация: принимает пароль в зашифрованном виде и закодированный в base64.
        Пароль должен быть зашифрован публичным клчом, выданным нашим сервисом (ручка /api/public-key).
        Возвращает модель данных по стандарту для OAuth2 авторизации.
        """

        return await self.do_authorize_unsafe(username, self.decrypt_password(passwd_encrypted), request=request)

    async def do_authorize_unsafe(self, username: str, passwd_plain: str, request: Request = None) -> Token:
        """
        Авторизация открытым паролем. Принимает пароль в открытом виде.
        Возвращает модель данных по стандарту для OAuth2 авторизации.

        Проверяет наличие пользователя в системе, что он не заблокирован и что хэш пароля в данных пользователя
        совпадает с хэшем переданного в метод пароля. Создает сессию пользователя, куда записывает данные по
        авторизации и bearer токен пользователя для дальнейшей авторизации по нему.
        """

        user = await UserRepo.get_user(username=username)

        if not user or user.disabled or user.is_robot or not self.verify_hash(passwd_plain, user.password):
            raise ForbiddenError(detail='Incorrect username or password')

        session = Session(
            sid=uuid4(),
            uid=user.uid,
            client_info={
                'addr': request.client.host,
                'user_agent': request.headers.get('User-Agent')
            }
        )

        await UserRepo.create_session(session)
        return Token(access_token=self.create_access_token(user.username, session.sid))

    async def do_logout(self, user: User):
        """ Выйти из текущего сеанса. Удаляет текущую сессию в таблице session """

        if user.curr_sid:
            await UserRepo.delete_sessions([user.curr_sid])

    async def close_another_sessions(self, user: User) -> int:
        """ Завершить все прочие сеансы пользователя кроме теущего """

        another_sessions = [s.sid for s in await UserRepo.get_user_sessions(user.uid) if s.sid != user.curr_sid]

        if another_sessions:
            await UserRepo.delete_sessions(another_sessions)

        return len(another_sessions)

    async def close_session(self, user: User, session_id: UUID):
        """ Завершить указанный сеанс. Проверяет, что сеанс принадлежит текущему пользователю """

        session = await UserRepo.get_session(session_id)

        if not session:
            raise NotFoundError(detail='Session not exists')

        if session.uid != user.uid:
            raise ForbiddenError(detail='Access denied')

        if session.sid == user.curr_sid:
            raise BadRequestError(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail='This is the current session. To close this, use the `logout`'
            )

        await UserRepo.delete_sessions([session_id])

    async def get_sessions(self, user: User) -> list[Session]:
        """ Получить все сессии пользователя """

        sessions = await UserRepo.get_user_sessions(user.uid)

        for session in sessions:
            if session.sid == user.curr_sid:
                session.is_current = True

        return sessions
