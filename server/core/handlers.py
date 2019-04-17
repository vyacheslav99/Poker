import os
import mimetypes

from . import config, utils
from .helpers import Request, Response, HTTPException


def index(request):
    return {'info': 'USSR Poker game server. Ver.: 1.0.0', 'ready': True}


def get_file(request):
    if request.is_json():
        #raise HTTPException(400, 'bad_request', 'application/json header is missing')
        file_name = request.json.get('file_name', '')
    else:
        file_name = request.params.get('file_name', '')

    file_path = os.path.normpath(os.path.join(config.DOCUMENT_ROOT, file_name))

    if os.path.isfile(file_path):
        resp = Response(200, 'OK', protocol=request.protocol,
                        headers={'Content-Type': utils.get_content_type(file_path),
                                 'Content-Disposition': f"attachment; filename={os.path.split(file_name)[1]}"})

        if request.method in ('GET', 'POST'):
            with open(file_path, 'rb') as f:
                resp.body = f.read()
        elif request.method == 'HEAD':
            resp.set_header('Content-Length', os.path.getsize(file_path))

        return resp
    else:
        raise HTTPException(404, 'not_found', f'Requested file <{file_name}> not found')
