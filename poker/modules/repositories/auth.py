from typing import Optional

from server.application import app
from models.player import Player
from models.auth import AuthRequest


class AuthRepo:

    @staticmethod
    def get_user_by_login_and_pwd(auth_params: AuthRequest) -> Optional[Player]:
        res = app.db.execute('select * from profiles where login = %(login)s and pass_hash = %(password)s',
                             params=auth_params.as_dict())
        return Player(**res) if res else None
