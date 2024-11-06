from fastapi import APIRouter
from api import config

router = APIRouter(tags=['base'])


@router.get('/is_alive')
async def is_alive():
    return {'server': config.SERVER_NAME, 'version': config.SERVER_VERSION, 'status': 'still alive'}


# @api.endpoint('/file', HttpMethods.GET)
# def download_file(request: Request):
#     file_name = request.params.get('file_name', '')
#
#     if not file_name:
#         raise HTTPException(400, message=f'Missing required parameter <file_name> in request query')
#
#     if file_name.startswith(('/', '\\')):
#         file_name = file_name[1:]
#
#     file_path = os.path.normpath(os.path.join(config.FILESTORE_DIR, file_name))
#
#     if os.path.isfile(file_path):
#         resp = Response(200, protocol=request.protocol,
#                         headers={'Content-Type': get_content_type(file_path),
#                                  'Content-Disposition': f"attachment; filename={os.path.split(file_name)[1]}"})
#
#         with open(file_path, 'rb') as f:
#             resp.body = f.read()
#
#         return resp
#     else:
#         raise HTTPException(404, message=f'Requested file <{file_name}> not found')
