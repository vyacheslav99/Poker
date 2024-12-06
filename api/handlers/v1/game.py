from uuid import UUID
from datetime import date
from fastapi import APIRouter, status, Query

from api.handlers.auth import RequiredAuthProvider
from api.models.game import (GameCreateBody, GameModel, GamePatchBody, GameOptions, Player, PlayerAddBody,
                             SetGameStatusBody, GameDateFilterFields, GameSortFields, GamesListResponse, GameStatusEnum)
from api.models.common import SuccessResponse, error_responses
from api.services.game import GameService

router = APIRouter(prefix='/games', tags=['game'])


@router.post(
    path='',
    response_model=GameModel,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новую игру',
    description='Создание новой игры на статусе Черновик',
    responses=error_responses()
)
async def create_game(user: RequiredAuthProvider, body: GameCreateBody):
    return await GameService().create_game(user, body)


@router.get(
    path='',
    response_model=GamesListResponse,
    summary='Список игр',
    description='Список игр с фильтрами и пагинацией. Поля фильтрации объединяются через AND',
    responses=error_responses()
)
async def get_games_list(
    user: RequiredAuthProvider,
    # game_ids: list[int] | None = Query(default=None, description='Список id игр'),
    code: str | None = Query(default=None, min_length=1, description='Код игры. Полное совпадение'),
    name: str | None = Query(default=None, min_length=3, description='Название игры. Поиск по частичному совпадению'),
    owner_id: UUID | None = Query(default=None, description='id пользователя владельца игры'),
    owner_name: str | None = Query(
        default=None, min_length=3, description='Имя пользователя владельца игры, поиск по частичномк совпадению'
    ),
    statuses: list[GameStatusEnum] | None = Query(default=None, description='Коды статусов игры'),
    date_from: date | None = Query(default=None, description='Дата "с" по полю date_field'),
    date_to: date | None = Query(default=None, description='Дата "по" по полю date_field'),
    date_field: GameDateFilterFields | None = Query(
        default=None, description='Поле дат, по которому фильтровать при помощи параметров date_from, date_to'
    ),
    sort_field: GameSortFields | None = Query(
        default='id', description='Поле сортировки. По умолчанию последние созданные игры сверху'
    ),
    sort_desc: bool | None = Query(default=True, description='Направление сортировки. По умолчанию "по убыванию"'),
    limit: int | None = Query(default=30, gt=0, description='Пагинация: количество строк на страницу. По умолчанию 30'),
    page: int | None = Query(
        default=1, gt=0, description='Пагинация: номер страницы, которую надо вернуть (по limit строк на странице, '
                                     'отсчет начинается с 1). По умолчанию 1'
    )
):
    return await GameService().get_games_list(
        user,
        # game_ids=game_ids,
        code=code,
        name=name,
        owner_id=owner_id,
        owner_name=owner_name,
        statuses=statuses,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        sort_field=sort_field,
        sort_desc=sort_desc,
        limit=limit,
        page=page
    )


@router.get(
    path='/{game_id}',
    response_model=GameModel,
    summary='Получить шапку игры',
    responses=error_responses()
)
async def get_game(user: RequiredAuthProvider, game_id: int):
    return await GameService().get_game(user, game_id)


@router.patch(
    path='/{game_id}',
    response_model=SuccessResponse,
    summary='Сохранить данные шапки игры',
    responses=error_responses()
)
async def set_game_data(user: RequiredAuthProvider, game_id: int, body: GamePatchBody):
    await GameService().set_game_data(user, game_id, body)
    return SuccessResponse()


@router.patch(
    path='/{game_id}/status',
    response_model=SuccessResponse,
    summary='Изменить статус игры',
    responses=error_responses()
)
async def set_game_status(user: RequiredAuthProvider, game_id: int, body: SetGameStatusBody):
    await GameService().set_game_status(user, game_id, body.status)
    return SuccessResponse()


@router.get(
    path='/{game_id}/options',
    response_model=GameOptions,
    summary='Получить договоренности',
    description='Получить договоренности по игре',
    responses=error_responses()
)
async def get_game_options(user: RequiredAuthProvider, game_id: int):
    return await GameService().get_game_options(user, game_id)


@router.put(
    path='/{game_id}/options',
    response_model=SuccessResponse,
    summary='Сохранить договоренности',
    description='Сохранить договоренности по игре',
    responses=error_responses()
)
async def set_game_options(user: RequiredAuthProvider, game_id: int, body: GameOptions):
    await GameService().set_game_options(user, game_id, body)
    return SuccessResponse()


@router.put(
    path='/{game_id}/player',
    response_model=list[Player],
    summary='Добавить игрока в игру',
    description='Добавить в игру еще одного игрока. Доступно добавление только игрока-ИИ (робота)',
    responses=error_responses()
)
async def add_player(user: RequiredAuthProvider, game_id: int, body: PlayerAddBody):
    return await GameService().add_player(user, game_id, body)


@router.delete(
    path='/{game_id}/player/{player_id}',
    response_model=list[Player],
    summary='Выгнать игрока из игры',
    responses=error_responses()
)
async def del_player(user: RequiredAuthProvider, game_id: int, player_id: UUID):
    return await GameService().del_player(user, game_id, player_id)
