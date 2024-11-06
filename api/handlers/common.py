from fastapi import APIRouter
from api import config

router = APIRouter(tags=['base'])


@router.get('/is_alive')
async def is_alive():
    return {'server': config.SERVER_NAME, 'version': config.SERVER_VERSION, 'status': 'still alive'}
