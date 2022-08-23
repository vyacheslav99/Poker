from domain.models.auth import AuthRequest, RegisterRequest
from domain.schemas.auth import AuthRequestBody
from api.modules.auth import Auth


class AuthController:

    @staticmethod
    def login(request):
        """
        :route: /api/v1/login
        :methods: post
        """

        return {'logined': Auth().login(AuthRequest(**request.json))}

    @staticmethod
    def register(request):
        """
        :route: /api/v1/register
        :methods: post
        """

        return {'user_uid': Auth().register(RegisterRequest(**request.json))}

    @staticmethod
    def logout(request):
        """
        :route: /api/v1/logout
        :methods: post
        """

        return 'success'