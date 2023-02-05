from server.router import Router
from server.helpers import Request,HttpMethods

api = Router('/api/v1')


@api.endpoint('/user', HttpMethods.POST)
def create_user(request: Request):
    pass
