from uuid import UUID
from fastapi import APIRouter, status

from api.handlers.auth import RequiredAuthProvider
from api.models.game import (GameCreateBody, GameModel, GamePatchBody, GameOptions, Player, PlayerAddBody,
                             SetGameStatusBody)
from api.models.common import SuccessResponse, error_responses
from api.services.game import GameService

router = APIRouter(prefix='/game', tags=['game'])


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
