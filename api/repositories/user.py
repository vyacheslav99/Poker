import json
import uuid

from api import db
from api.db.expressions import condition
from api.models.user import User, Session
from api.models.exceptions import NoChangesError


class UserRepo:

    _protected_user_fileds = ['uid']

    @staticmethod
    async def get_user(user_id: uuid.UUID | str = None, username: str = None) -> User | None:
        if not user_id and not username:
            raise Exception('Один из параметров должен быть передан: user_id or username')

        conditions = db.expressions.condition()

        if user_id:
            conditions.and_x('uid = %(uid)s', uid=user_id)
        if username:
            conditions.and_x('username = %(username)s', username=username)

        row = await db.fetchone(f'select * from users where {conditions}', **conditions.values)
        return User(**row) if row else None

    @staticmethod
    async def create_user(user: User) -> User:
        sql = """
        insert into users (uid, username, fullname, password)
        values (%(uid)s, %(username)s, %(fullname)s, %(password)s)
        returning *
        """

        res = await db.fetchone(sql, **user.model_dump())
        return User(**res) if res else None

    @staticmethod
    async def update_user(user_id: uuid.UUID, **data) -> User:
        fields = db.expressions.set()

        for k, v in data.items():
            if k not in UserRepo._protected_user_fileds:
                fields.field(k, v)

        if not fields.values:
            raise NoChangesError('Nothing to change')

        sql = f"""
        update users set
        {fields}
        where uid = %(uid)s
        returning *
        """

        row = await db.fetchone(sql, uid=user_id, **fields.values)
        return User(**row) if row else None

    @staticmethod
    async def get_session(session_id: uuid.UUID) -> Session | None:
        sql = """
        select s.*, u.username
        from session s
            join users u on u.uid = s.uid
        where s.sid = %(sid)s
        """

        row = await db.fetchone(sql, sid=session_id)
        return Session(**dict(row, client_info=json.loads(row['client_info']))) if row else None

    @staticmethod
    async def get_user_sessions(user_id: uuid.UUID) -> list[Session]:
        sql = """
        select s.*, u.username
        from session s
            join users u on u.uid = s.uid
        where s.uid = %(uid)s
        """

        data = await db.fetchall(sql, uid=user_id)
        return [Session(**dict(row, client_info=json.loads(row['client_info']))) for row in data]

    @staticmethod
    async def create_session(session: Session):
        sql = """
        insert into session (sid, uid, client_info)
        values (%(sid)s, %(uid)s, %(client_info)s)
        """

        await db.execute(
            sql, client_info=json.dumps(session.client_info), **session.model_dump(exclude={'client_info'})
        )

    @staticmethod
    async def delete_sessions(session_ids: list[uuid.UUID]):
        await db.execute('delete from session where sid = any(%(session_ids)s)', session_ids=session_ids)
