from uuid import UUID

from api import db
from api.db.expressions import condition
from api.models.game import GameCreateBody, GameModel, GameStatusEnum
from api.models.user import UserPublic


class GameRepo:

    @staticmethod
    async def create_game(owner_id: UUID, params: GameCreateBody) -> GameModel:
        sql = """
        insert into games (code, name, players_cnt, owner_id, status)
        values (%(code)s, %(name)s, %(players_cnt)s, %(owner_id)s, %(status)s)
        returning *
        """

        sql_add_player = 'insert into game_players (game_id, player_id) values (%(game_id)s, %(player_id)s)'

        async with db.connection() as con, con.transaction():
            row = await con.fetchone(sql, owner_id=owner_id, status=GameStatusEnum.DRAFT, **params.model_dump())
            res = GameModel(players=[], **row)
            await con.execute(sql_add_player, game_id=res.id, player_id=owner_id)

        return res

    @staticmethod
    async def get_game(game_id: int) -> GameModel | None:
        sql = """
        select g.*,
            jsonb_agg(
                json_build_object('uid', u.uid, 'username', u.username, 'fullname', u.fullname, 'avatar', u.avatar)
            ) as players
        from games g
            left join game_players gp on gp.game_id = g.id
            left join users u on u.uid = gp.player_id
        where g.id = 1
        group by g.id        
        """

        row = await db.fetchone(sql, game_id=game_id)
        return GameModel.make(dict(row)) if row else None

    @staticmethod
    async def get_game_players(game_id: int) -> list[UserPublic]:
        sql = """
        select u.uid, u.username, u.fullname, u.avatar
        from game_players gp
            join users u on u.uid = gp.player_id
        where gp.game_id = %(game_id)s
        """

        data = await db.fetchall(sql, game_id=game_id)
        return [UserPublic(**row) for row in data]
