import os

from . import config, utils
from .helpers import Response, HTTPException


def index(request):
    return {'info': 'USSR Poker game server. Ver.: 1.0.0', 'ready': True}


def get_file(request):
    # todo: Перенести весь этот функционал в ядро игры, здесь оставить только дергание соотв. функции
    # пока что файлы не выдаем, т.к. непонятно, какие вобще выдавать, и будет ли вобще такая надобность
    raise HTTPException(403, 'Forbidden', 'forbidden', 'Forbidden')

    # if request.method == 'POST':
    #     if request.is_json():
    #         file_name = request.json.get('file_name', '')
    #     else:
    #         raise HTTPException(400, 'Bad Request', 'bad_request', 'application/json header is missing')
    # else:  # GET
    #     file_name = request.params.get('file_name', '')
    #
    # if file_name.startswith(('/', '\\')):
    #     file_name = file_name[1:]
    #
    # file_path = os.path.normpath(os.path.join(config.DOCUMENT_ROOT, file_name))
    #
    # if os.path.isfile(file_path):
    #     resp = Response(200, 'OK', protocol=request.protocol,
    #                     headers={'Content-Type': utils.get_content_type(file_path),
    #                              'Content-Disposition': f"attachment; filename={os.path.split(file_name)[1]}"})
    #
    #     with open(file_path, 'rb') as f:
    #         resp.body = f.read()
    #     # elif request.method == 'HEAD':
    #     #     resp.set_header('Content-Length', os.path.getsize(file_path))
    #
    #     return resp
    # else:
    #     raise HTTPException(404, 'Not Found', 'file_not_exists', f'Requested file <{file_name}> not found')
