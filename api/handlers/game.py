from fastapi import APIRouter, status

from api.handlers import RequiredAuthProvider
from api.models.game import GameCreateBody, GameModel
from api.models.common import SuccessResponse, error_responses
from api.services.game import GameService

router = APIRouter(prefix='/api', tags=['game'])


@router.post(
    path='/game',
    response_model=GameModel,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новую игру',
    description='Создание новой игры на статусе Черновик',
    responses=error_responses()
)
async def create_game(user: RequiredAuthProvider, body: GameCreateBody):
    return await GameService().create_game(user, body)
