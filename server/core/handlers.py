import os
import mimetypes

from .helpers import Request, Response


def index(request):
    return {'info': 'USSR Poker game server. Ver.: 1.0.0', 'ready': True}


def get_content_type(file_name):
    return mimetypes.guess_type(file_name)[0] or 'application/octet-stream'


# так вернем файл, если надо будет
# return self._create_file_response(self.request.method, os.path.join(path, 'index.html'))
# return self._create_file_response(self.request.method, 'index.html',
#                                   file_data=self._render_directory_index(path))
def create_file_response(request, file_name, file_data=None):
    resp = Response(200, 'OK', protocol=request.protocol, headers={'Content-Type': get_content_type(file_name)})

    if not file_data and request.method in ('GET', 'POST'):
        with open(file_name, 'rb') as f:
            file_data = f.read()

    if request.method in ('GET', 'POST'):
        resp.body = file_data

    resp.set_header('Content-Length',
                    len(file_data) or (os.path.getsize(file_name) if os.path.exists(file_name) else 0))

    return resp
