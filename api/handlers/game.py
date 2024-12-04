from fastapi import APIRouter, status

from api.handlers import RequiredAuthProvider
from api.models.user import UserPublic
from api.models.game import GameCreateBody, GameModel, GamePatchBody, GameOptions, PlayerAddBody
from api.models.common import SuccessResponse, error_responses
from api.services.game import GameService

router = APIRouter(prefix='/api/game', tags=['game'])


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
    response_model=list[UserPublic],
    summary='Добавить игрока в игру',
    description='Добавить в игру еще одного игрока. Доступно добавление только игрока-ИИ (робота)',
    responses=error_responses()
)
async def add_player(user: RequiredAuthProvider, game_id: int, body: PlayerAddBody):
    return await GameService().add_player(user, game_id, body)
