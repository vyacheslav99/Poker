import os

from configs import config
from server.helpers import Request, Response, HTTPException, HttpMethods, get_content_type, CONTENT_TYPE_PEM
from server.router import Router
from api.modules.security import AuthorizationRequiredProvider

api = Router()


@api.endpoint('/is_alive', [HttpMethods.HEAD, HttpMethods.GET])
def is_alive(request: Request):
    if request.method == HttpMethods.HEAD:
        return None

    return {'server': 'Poker game server', 'version': '1.0.0', 'status': 'still alive'}


@api.endpoint('/public-key', HttpMethods.GET, security=(AuthorizationRequiredProvider(),))
def get_public_key(request: Request):
    if config.RSA_PUBLIC_KEY:
        return Response(200, headers={'Content-Type': CONTENT_TYPE_PEM}, body=config.RSA_PUBLIC_KEY)

    raise HTTPException(404, message='No public keys found')


@api.endpoint('/file', HttpMethods.GET)
def download_file(request: Request):
    file_name = request.params.get('file_name', '')

    if not file_name:
        raise HTTPException(400, message=f'Missing required parameter <file_name> in request query')

    if file_name.startswith(('/', '\\')):
        file_name = file_name[1:]

    file_path = os.path.normpath(os.path.join(config.FILESTORE_DIR, file_name))

    if os.path.isfile(file_path):
        resp = Response(200, protocol=request.protocol,
                        headers={'Content-Type': get_content_type(file_path),
                                 'Content-Disposition': f"attachment; filename={os.path.split(file_name)[1]}"})

        with open(file_path, 'rb') as f:
            resp.body = f.read()

        return resp
    else:
        raise HTTPException(404, message=f'Requested file <{file_name}> not found')
