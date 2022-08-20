from server.helpers import HTTPException
from api.repositories.auth import AuthRepo
from domain.models.auth import AuthRequest, RegisterRequest


class Auth:

    def login(self, auth_params: AuthRequest) -> str:
        res = AuthRepo.get_user_by_login_and_pwd(auth_params)

        if not res:
            raise HTTPException(401, 'Unauthorized')

        return res.uid

    def register(self, player: RegisterRequest) -> str:
        res = AuthRepo.create_player(player)
        return res.uid