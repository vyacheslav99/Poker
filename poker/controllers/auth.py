from server.helpers import HTTPException
from models.auth import AuthRequest, RegisterRequest
from modules.auth import Auth


class AuthController(object):

    @staticmethod
    def login(request):
        """
        :route: /api/v1/login
        :methods: post
        """

        return {'user_uid': Auth().login(AuthRequest(**request.json))}

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