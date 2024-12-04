from typing import Annotated
from fastapi import APIRouter, Query

from api.handlers import OptionalAuthProvider
from api.models.statistics import OverallStatisticsResponse, StatisticsSortFields
from api.models.common import SuccessResponse, error_responses
from api.services.misc import MiscService


router = APIRouter(prefix='/api', tags=['misc'])


@router.get(
    path='/is_free_username',
    response_model=SuccessResponse,
    summary='Проверить логин',
    description='Проверить, свободен ли переданный логин. Полезно сделать перед регистрацией пользователя на клиенте, '
                'чтоб не получить ошибку регистрации пользователя',
    response_description='Вернет `success: false` если логин занят иначе `true`',
    responses=error_responses()
)
async def username_is_free(username: str):
    is_free = await MiscService().username_is_free(username)
    return SuccessResponse(success=is_free)


@router.get(
    path='/statistics',
    response_model=OverallStatisticsResponse,
    summary='Статистика игроков (таблица лучших)',
    description='Получить статистику по результатам лучших игроков + текущего авторизованного пользователя, '
                'если авторизован + переданных на вход игроков по их id',
    responses=error_responses()
)
async def get_overall_statistics(
    user: OptionalAuthProvider, include_user_ids: Annotated[list[str] | None, Query()] = None,
    sort_field: StatisticsSortFields = None, sort_desc: bool = None, limit: int = None
):
    data = await MiscService().get_statistics(
        user=user, include_user_ids=include_user_ids, sort_field=sort_field, sord_desc=sort_desc, limit=limit
    )

    return OverallStatisticsResponse(items=data, total=len(data))
