import os

from fastapi import HTTPException, status, UploadFile
from fastapi.exceptions import RequestValidationError

from api import config
from api.models.security import User
from api.models.user import UserPatchBody
from api.models.exceptions import NoChangesError
from api.models.http import AVAILABLE_IMAGE_TYPES
from api.repositories.user import UserRepo


class UserService:

    async def change_user(self, user: User, data: UserPatchBody) -> User:
        try:
            return await UserRepo.update_user(user.uid, **data.model_dump(exclude_unset=True))
        except NoChangesError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def change_avatar(self, user: User, file: UploadFile) -> User:
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
        if not user.avatar:
            return user

        file_path = os.path.join(config.FILESTORE_DIR, user.avatar)

        if os.path.exists(file_path):
            os.remove(file_path)

        return await UserRepo.update_user(user.uid, avatar=None)
