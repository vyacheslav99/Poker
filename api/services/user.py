from fastapi import HTTPException, status

from api.models.security import User
from api.models.user import UserPatchBody
from api.models.exceptions import NoChangesError
from api.repositories.user import UserRepo


class UserService:

    async def change_user(self, user: User, data: UserPatchBody) -> User:
        try:
            return await UserRepo.update_user(user.uid, **data.model_dump(exclude_unset=True))
        except NoChangesError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
