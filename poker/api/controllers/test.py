from server.router import handler
from domain.models.auth import AuthRequest
from domain.schemas.auth import AuthRequestBody
from api.modules.auth import Auth


@handler(
    path='/api/v1/login',
    methods='post',
    body_schema=AuthRequestBody
)
def login(request):
    return {'logined': Auth().login(AuthRequest(**request.json))}
