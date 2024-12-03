import secrets

from api.models.game import GameCreateBody, GameModel
from api.models.user import User
from api.repositories.game import GameRepo


class GameService:

    async def create_game(self, user: User, params: GameCreateBody) -> GameModel:
        if not params.code:
            params.code = secrets.token_urlsafe(8)

        game = await GameRepo.create_game(user.uid, params)
        game.players = await GameRepo.get_game_players(game.id)
        return game
