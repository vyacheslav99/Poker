import json
import uuid

from api import db
from api.db.expressions import condition
from api.models.security import UserDTO, Session


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

        row = await db.fetchone(f'select * from users where {conditions}', **conditions.values)
        return UserDTO(**row) if row else None

    @staticmethod
    async def create_user(user: UserDTO) -> UserDTO:
        sql = """
        insert into users (uid, username, fullname, password)
        values (%(uid)s, %(username)s, %(fullname)s, %(password)s)
        returning *
        """

        res = await db.fetchone(sql, **user.model_dump())
        return UserDTO(**res) if res else None

    @staticmethod
    async def get_session(sid: uuid.UUID) -> Session | None:
        sql = """
        select s.*, u.username
        from session s
            join users u on u.uid = s.uid 
        where s.sid = %(sid)s
        """

        row = await db.fetchone(sql, sid=sid)
        return Session(**dict(row, client_info=json.loads(row['client_info']))) if row else None

    @staticmethod
    async def create_session(session: Session):
        sql = """
        insert into session (sid, uid, client_info)
        values (%(sid)s, %(uid)s, %(client_info)s)
        """

        await db.execute(
            sql, client_info=json.dumps(session.client_info), **session.model_dump(exclude={'client_info'})
        )
