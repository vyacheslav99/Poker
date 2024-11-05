import uuid

from api import db
from api.db.expressions import condition
from api.models.user import UserDTO


class UserRepo:

    @staticmethod
    async def get_user(user_id: uuid.UUID | str = None, username: str = None) -> UserDTO | None:
        if not user_id and not username:
            raise Exception('Один из параметров должен быть передан: user_id or username')

        conditions = db.expressions.condition()

        if user_id:
            conditions.and_x('uid = %(uid)s', uid=user_id)
        if username:
            conditions.and_x('username = %(username)s', username=username)

        data = await db.fetchone(f'select * from users where {conditions}', **conditions.values)
        return UserDTO(**data) if data else None

    @staticmethod
    async def create_user(user: UserDTO) -> UserDTO:
        sql = """
        insert into users (uid, username, fullname, password, avatar)
        values (%(uid)s, %(username)s, %(fullname)s, %(password)s, %(avatar)s)
        returning *
        """

        res = await db.fetchone(sql, **user.model_dump())
        return UserDTO(**res) if res else None
