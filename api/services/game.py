import secrets

from datetime import datetime, timezone
from uuid import UUID

from api.models.game import GameCreateBody, GameModel, GamePatchBody, GameOptions, PlayerAddBody, GameStatusEnum
from api.models.user import User, UserPublic
from api.models.exceptions import NotFoundError, ForbiddenError, NoChangesError, ConflictError, BadRequestError
from api.repositories.game import GameRepo
from api.repositories.user import UserRepo


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
        game = await self.get_game(user, game_id, access_only_owner=True)

        if not game.allow_edit():
            raise ConflictError('Изменение игры на данном статусе запрещено')

        if data.players_cnt is not None and data.players_cnt < len(game.players):
            raise ConflictError(
                'Невозможно установить количество игроков в игре меньшим, чем количество уже добавленных '
                'игроков. Сначала удалите лишнего игрока из списка'
            )

        try:
            await GameRepo.set_game_data(game_id, **data.model_dump(exclude_unset=True))
        except NoChangesError as e:
            raise BadRequestError(detail=str(e))

    async def set_game_status(self, user: User, game_id: int, status: GameStatusEnum):
        game = await self.get_game(user, game_id, access_only_owner=True)

        if status == game.status:
            return

        if not game.status.allow_pass_to(status):
            raise ConflictError('Невозможно перейти на данный статус')

        extra_data = {}

        if status == GameStatusEnum.STARTED and not game.status in GameStatusEnum.playing_statuses():
            extra_data['started_at'] = datetime.now(tz=timezone.utc)
        elif status == GameStatusEnum.STARTED and game.status == GameStatusEnum.PAUSED:
            extra_data['resumed_at'] = datetime.now(tz=timezone.utc)
        elif status == GameStatusEnum.PAUSED and game.status == GameStatusEnum.STARTED:
            extra_data['paused_at'] = datetime.now(tz=timezone.utc)
        elif status in (GameStatusEnum.FINISHED, GameStatusEnum.ABORTED):
            extra_data['finished_at'] = datetime.now(tz=timezone.utc)

        try:
            await GameRepo.set_game_data(game_id, status=status, **extra_data)
        except NoChangesError as e:
            raise BadRequestError(detail=str(e))

    async def get_game_options(self, user: User, game_id: int) -> GameOptions:
        await self.get_game(user, game_id)
        opts = await GameRepo.get_game_options(game_id)

        if not opts:
            raise NotFoundError(detail='Game options have not been set yet')

        return opts

    async def set_game_options(self, user: User, game_id: int, options: GameOptions):
        game = await self.get_game(user, game_id, access_only_owner=True)

        if not game.allow_edit():
            raise ConflictError('Изменение игры на данном статусе запрещено')

        await GameRepo.set_game_options(game_id, options)

    async def add_player(self, user: User, game_id: int, data: PlayerAddBody) -> list[UserPublic]:
        game = await self.get_game(user, game_id, access_only_owner=True)

        if not game.allow_edit():
            raise ConflictError('Изменение игры на данном статусе запрещено')

        if len(game.players) >= game.players_cnt:
            raise ConflictError('Все места в игре уже заполнены')

        player = await UserRepo.get_user(user_id=data.user_id, username=data.username)

        if not player:
            raise NotFoundError('Такого игрока не существует')

        if not player.is_robot:
            raise ConflictError('Вы можете добавлять только игроков-ИИ (роботов)')

        for p in game.players:
            if p.uid == player.uid:
                raise ConflictError('Такой игрок уже есть среди участников игры')

        await GameRepo.add_player(game_id, player.uid)
        return await GameRepo.get_game_players(game_id)

    async def del_player(self, user: User, game_id: int, player_id: UUID) -> list[UserPublic]:
        game = await self.get_game(user, game_id, access_only_owner=True)

        if not game.allow_edit():
            raise ConflictError('Изменение игры на данном статусе запрещено')

        await GameRepo.del_player(game_id, player_id)
        return await GameRepo.get_game_players(game_id)
