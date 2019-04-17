import os
import mimetypes

from . import config
from .helpers import Request, Response, HTTPException


def index(request):
    return {'info': 'USSR Poker game server. Ver.: 1.0.0', 'ready': True}


def get_content_type(file_name):
    return mimetypes.guess_type(file_name)[0] or 'application/octet-stream'


def get_file(request):
    if not request.is_json():
        raise HTTPException(400, 'bad_request', 'application/json header is missing')

    file_path = os.path.normpath(os.path.join(config.DOCUMENT_ROOT, request.json.get('file_name', '')))

    if os.path.isfile(file_path):
        resp = Response(200, 'OK', protocol=request.protocol, headers={'Content-Type': get_content_type(file_path)})

        if request.method in ('GET', 'POST'):
            with open(file_path, 'rb') as f:
                resp.body = f.read()
        elif request.method == 'HEAD':
            resp.set_header('Content-Length', os.path.getsize(file_path))

        return resp
    else:
        raise HTTPException(404, 'not_found', f'Requested file <{request.json.get("file_name", "")}> not found')
