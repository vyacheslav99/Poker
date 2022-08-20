from typing import Optional

from server.helpers import HTTPException
from modules.repositories.auth import AuthRepo
from models.auth import AuthRequest


class Auth:

    def login(self, auth_params: AuthRequest) -> Optional[str]:
        res = AuthRepo.get_user_by_login_and_pwd(auth_params)

        if not res:
            raise HTTPException(401, 'Unauthorized')

        return res.uid
