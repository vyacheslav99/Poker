import secrets

from api.models.game import GameCreateBody, GameModel, GamePatchBody, GameOptions
from api.models.user import User
from api.models.exceptions import NotFoundError, ForbiddenError, NoChangesError, BadRequestError
from api.repositories.game import GameRepo


class GameService:

    async def create_game(self, user: User, data: GameCreateBody) -> GameModel:
        if not data.code:
            data.code = secrets.token_urlsafe(8)

        game = await GameRepo.create_game(user.uid, data)
        game.players = await GameRepo.get_game_players(game.id)
        return game

    async def get_game(self, user: User, game_id: int, access_only_owner: bool = False) -> GameModel:
        game = await GameRepo.get_game(game_id)

        if not game:
            raise NotFoundError(detail='Game not found')

        if game.owner_id != user.uid:
            if access_only_owner:
                raise ForbiddenError()
            else:
                game.code = None

        for uid in set([u.uid for u in game.players] + [game.owner_id]):
            if uid == user.uid:
                break
        else:
            raise ForbiddenError()

        return game

    async def set_game_data(self, user: User, game_id: int, data: GamePatchBody):
        await self.get_game(user, game_id, access_only_owner=True)

        try:
            await GameRepo.set_game_data(game_id, **data.model_dump(exclude_unset=True))
        except NoChangesError as e:
            raise BadRequestError(detail=str(e))

    async def get_game_options(self, user: User, game_id: int) -> GameOptions:
        await self.get_game(user, game_id)

        opts = await GameRepo.get_game_options(game_id)

        if not opts:
            raise NotFoundError(detail='Game options have not been set yet')

        return opts

    async def set_game_options(self, user: User, game_id: int, options: GameOptions):
        await self.get_game(user, game_id, access_only_owner=True)
        await GameRepo.set_game_options(game_id, options)
