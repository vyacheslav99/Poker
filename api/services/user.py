import os
import uuid

from fastapi import HTTPException, status, UploadFile
from fastapi.exceptions import RequestValidationError
from asyncpg.exceptions import UniqueViolationError

from api import config
from api.models.user import User, UserPatchBody
from api.models.security import Token, LoginBody
from api.models.exceptions import NoChangesError
from api.models.http import AVAILABLE_IMAGE_TYPES
from api.services.security import Security
from api.repositories.user import UserRepo


class UserService:

    def __init__(self):
        self._sec = Security()

    async def create_user(self, user: LoginBody) -> User:
        """
        Создание нового пользователя.
        Пароль принимает в зашифрованном виде и закодированный в base64.
        Пароль должен быть зашифрован публичным клчом, выданным нашим сервисом (ручка /api/public-key).
        Возвращает модель пользователя.
        """

        return await UserRepo.create_user(User(
            uid=uuid.uuid4(),
            username=user.username,
            password=self._sec.calc_hash(self._sec.decrypt_password(user.password)),
            fullname=user.username
        ))

    async def delete_user(self, user: User, passwd_encrypted: str):
        """
        Удаление пользователя

        Полное физическое удаление пользователя из системы со всеми сопутствующими потрохами:
        - сессиями
        - статистикой
        - файлами (аватаркой)
        - играми, где он создатель/владелец
        - удаление его как участника из игр, где он участник
        - что-то еще?

        На всякий случай при удалении проверяем текущий пароль
        """

        if not self._sec.verify_hash(self._sec.decrypt_password(passwd_encrypted), user.password):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Incorrect password')

        await self.clear_avatar(user)
        # todo: Не забывать при появлении новых связей по пользователю добавлять сюда их удаление
        #  (если они не каскадные)
        await UserRepo.delete_user(user.uid)

    async def change_password(
        self, user: User, old_pwd_encrypted: str, new_pwd_encrypted: str, close_sessions: bool = False
    ):
        """
        Смена пароля пользователя.
        Пароли передаем в зашифрованном виде.
        Завершает все прочие сеансы, кроме текущего, если указан флаг close_sessions
        """

        old_passwd = self._sec.decrypt_password(old_pwd_encrypted)

        if not self._sec.verify_hash(old_passwd, user.password):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Incorrect password')

        await UserRepo.update_user(
            user.uid, password=self._sec.calc_hash(self._sec.decrypt_password(new_pwd_encrypted))
        )

        if close_sessions:
            await self._sec.close_another_sessions(user)

    async def change_username(self, user: User, new_username: str) -> Token:
        """
        Изменение логина пользователя.

        Так как логин зашит в авторизационном токне, то все существующие токены автоматически становятся
        недействительными (при авторизации юзер не будет найден в БД). Поэтому:
        1. Удалить все существующие сеансы, кроме текущего.
        2. По текущему сеансу перевыпустить токен: создать новый с новым логином и текущим id сессии
        3. Вернуь новый токен
        """

        try:
            _user = await UserRepo.update_user(user.uid, username=new_username)
        except UniqueViolationError:
            raise HTTPException(status.HTTP_409_CONFLICT, detail=f'Username <{new_username}> already exists')

        await self._sec.close_another_sessions(user)
        return Token(access_token=self._sec.create_access_token(_user.username, user.curr_sid))

    async def change_user(self, user: User, data: UserPatchBody) -> User:
        """
        Изменение прочих данных пользователя (fullname и т.п. - пока только одно это поле)
        Изменяет только поля, явно переданные в запросе, остальные оставляет нетронутыми
        """

        try:
            return await UserRepo.update_user(user.uid, **data.model_dump(exclude_unset=True))
        except NoChangesError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def change_avatar(self, user: User, file: UploadFile) -> User:
        """
        Изменить аватарку пользователя
        Сохраняет переданный файл на диск и записывает его в данные пользователя
        """

        ext = os.path.splitext(file.filename)[1]

        if ext.lower() not in AVAILABLE_IMAGE_TYPES:
            raise RequestValidationError(
                [{'file': f"Usupported file type. Acceptable types: {', '.join(AVAILABLE_IMAGE_TYPES)}"}]
            )

        file_name = f'{str(user.uid)}{ext}'
        file_path = os.path.join(config.FILESTORE_DIR, file_name)
        await file.seek(0)

        with open(file_path, 'wb') as f:
            f.write(await file.read())

        return await UserRepo.update_user(user.uid, avatar=file_name)

    async def clear_avatar(self, user: User) -> User:
        """
        Удалить аватарку пользователя
        Удаляет файл и затирает его в данных пользователя
        """

        if not user.avatar:
            return user

        file_path = os.path.join(config.FILESTORE_DIR, user.avatar)

        if os.path.exists(file_path):
            os.remove(file_path)

        return await UserRepo.update_user(user.uid, avatar=None)
