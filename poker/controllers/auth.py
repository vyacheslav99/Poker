import uuid

from schemas.auth import AuthRequestBody
from server.helpers import HTTPException


class AuthController(object):

    @staticmethod
    def auth(request):
        """
        :route: /api/v1/auth
        :methods: post
        """

        AuthRequestBody().load(request.json)
        return {'user_id': uuid.uuid4().hex}

    @staticmethod
    def logout(request):
        """
        :route: /api/v1/logout
        :methods: post
        """

        if 'user_id' not in request.headers:
            raise HTTPException(401, 'Unauthorized', message='Да ты в общем-то и не авторизован')

        return 'success'