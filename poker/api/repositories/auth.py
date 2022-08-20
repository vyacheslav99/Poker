import uuid

from typing import Optional

from server.application import app
from domain.models import Player
from domain.models import AuthRequest, RegisterRequest


class AuthRepo:

    @staticmethod
    def get_user_by_login_and_pwd(auth_params: AuthRequest) -> Optional[Player]:
        res = app.db.fetchone('select * from profiles where login = %(login)s and pass_hash = %(password)s',
                              params=auth_params.as_dict())
        return Player(**res) if res else None

    @staticmethod
    def create_player(player: RegisterRequest) -> Optional[Player]:
        sql = '''
            insert into profiles (uid, login, pass_hash, name)
            values (%(uid)s::uuid, %(login)s, %(password)s, %(name)s)
            returning *
        '''

        res = app.db.execute(sql, params=dict(uid=uuid.uuid4().hex, **player.as_dict()))
        return Player(**res) if res else None