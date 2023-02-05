from server.helpers import Request, HTTPException, SecurityProvider


class AuthorizationRequiredProvider(SecurityProvider):

    def exec(self, request: Request):
        if not request.headers.get('Authorization'):
            raise HTTPException(401, message='Authorization required')
