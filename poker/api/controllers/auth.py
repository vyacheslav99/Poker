from domain.models.auth import AuthRequest, RegisterRequest
from domain.schemas.auth import AuthRequestBody, RegisterRequestBody, UserUIDResponse
from api.modules.auth import Auth
from api.modules.utils import schemas_definition


class AuthController:

    @staticmethod
    @schemas_definition(body_schema=AuthRequestBody, response_schema=UserUIDResponse)
    def login(request):
        """
        :route: /api/v1/login
        :methods: post
        """

        return {'user_uid': Auth().login(AuthRequest(**request.json))}, 'ok', 200

    @staticmethod
    @schemas_definition(body_schema=RegisterRequestBody, response_schema=UserUIDResponse)
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