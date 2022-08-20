from server.helpers import HTTPException
from models.auth import AuthRequest
from modules.auth import Auth


class AuthController(object):

    @staticmethod
    def login(request):
        """
        :route: /api/v1/login
        :methods: post
        """

        uid = Auth().login(AuthRequest(**request.json))
        return {'user_id': uid}

    @staticmethod
    def logout(request):
        """
        :route: /api/v1/logout
        :methods: post
        """

        return 'success'