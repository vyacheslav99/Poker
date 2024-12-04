from fastapi import APIRouter
from api import config

router = APIRouter(tags=['base'])


@router.get(
    path='/is_alive',
    response_model=dict,
    summary='Пинг сервера',
    description='Проверка доступности сервера + получение информации о том, что за сервер, для идентификации его '
                'клиентом'
)
async def is_alive():
    return {'server': config.SERVER_NAME, 'version': config.SERVER_VERSION, 'status': 'still alive'}
