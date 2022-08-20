import os

from configs import config
from models.request import HttpMethods
from server.helpers import Response, HTTPException
from modules import utils


class CommonController:

    @staticmethod
    def is_alive(request):
        """
        :route: /api/v1/is_alive
        :methods: get, head
        """

        if request.method == HttpMethods.HEAD:
            return None

        return 'Still alive'

    @staticmethod
    def download_file(request):
        """
        :route: /api/v1/file
        :methods: get
        """

        file_name = request.params.get('file_name', '')

        if not file_name:
            raise HTTPException(400, 'Bad Request', message=f'Missing required parameter <file_name> in request query')

        if file_name.startswith(('/', '\\')):
            file_name = file_name[1:]

        file_path = os.path.normpath(os.path.join(config.DOCUMENT_ROOT, file_name))

        if os.path.isfile(file_path):
            resp = Response(200, 'OK', protocol=request.protocol,
                            headers={'Content-Type': utils.get_content_type(file_path),
                                     'Content-Disposition': f"attachment; filename={os.path.split(file_name)[1]}"})

            with open(file_path, 'rb') as f:
                resp.body = f.read()

            return resp
        else:
            raise HTTPException(404, 'Not Found', message=f'Requested file <{file_name}> not found')
