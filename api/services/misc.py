from uuid import UUID

from api.models.user import User
from api.models.statistics import UserStatistics
from api.repositories.user import UserRepo
from api.repositories.misc import MiscRepo


class MiscService:

    async def username_is_free(self, username: str) -> bool:
        user = await UserRepo.get_user(username=username)
        return False if user else True

    async def get_statistics(
        self, user: User = None, include_user_ids: list[UUID] = None, sort_field: str = None, sord_desc: bool = None,
        limit: int = None
    ) -> list[UserStatistics]:
        include_user_ids = include_user_ids or []

        if user and user.uid not in include_user_ids:
            include_user_ids.append(user.uid)

        return await MiscRepo.get_statistics(
            include_user_ids=include_user_ids, sort_field=sort_field or 'summary',
            sord_desc=sord_desc if sord_desc is not None else True, limit=limit or 20
        )
