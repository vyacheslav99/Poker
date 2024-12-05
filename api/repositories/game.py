from uuid import UUID

from api import db
from api.db.expressions import condition
from api.models.game import GameCreateBody, GameModel, GameStatusEnum, GameOptions
from api.models.exceptions import NoChangesError
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
            jsonb_agg(json_build_object(
                'uid', u.uid, 'username', u.username, 'fullname', u.fullname, 'avatar', u.avatar, 'is_robot', u.is_robot
            )) as players
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
        select u.uid, u.username, u.fullname, u.avatar, u.is_robot
        from game_players gp
            join users u on u.uid = gp.player_id
        where gp.game_id = %(game_id)s
        """

        data = await db.fetchall(sql, game_id=game_id)
        return [UserPublic(**row) for row in data]

    @staticmethod
    async def set_game_data(game_id: int, **data):
        fields = db.expressions.set()

        for k, v in data.items():
            fields.field(k, v)

        if not fields.values:
            raise NoChangesError('Nothing to change')

        sql = f"""
        update games set
            {fields}
        where id = %(game_id)s
        """

        await db.execute(sql, game_id=game_id, **fields.values)

    @staticmethod
    async def get_game_options(game_id: int) -> GameOptions | None:
        sql = 'select * from game_options where game_id = %(game_id)s'

        row = await db.fetchone(sql, game_id=game_id)
        return GameOptions(**row) if row else None

    @staticmethod
    async def set_game_options(game_id: int, options: GameOptions):
        sql = """
        insert into game_options (game_id, game_sum_by_diff, dark_allowed, third_pass_limit, fail_subtract_all,
            no_joker, joker_give_at_par, joker_demand_peak, pass_factor, gold_mizer_factor, dark_notrump_factor,
            brow_factor, dark_mult, gold_mizer_on_null, on_all_order, take_block_bonus, bet, players_cnt, deal_types)
        values (%(game_id)s, %(game_sum_by_diff)s, %(dark_allowed)s, %(third_pass_limit)s, %(fail_subtract_all)s,
            %(no_joker)s, %(joker_give_at_par)s, %(joker_demand_peak)s, %(pass_factor)s, %(gold_mizer_factor)s,
            %(dark_notrump_factor)s, %(brow_factor)s, %(dark_mult)s, %(gold_mizer_on_null)s, %(on_all_order)s,
            %(take_block_bonus)s, %(bet)s, %(players_cnt)s, %(deal_types)s)
        on conflict on constraint game_options_pk do update set
            game_sum_by_diff = excluded.game_sum_by_diff,
            dark_allowed = excluded.dark_allowed,
            third_pass_limit = excluded.third_pass_limit,
            fail_subtract_all = excluded.fail_subtract_all,
            no_joker = excluded.no_joker,
            joker_give_at_par = excluded.joker_give_at_par,
            joker_demand_peak = excluded.joker_demand_peak,
            pass_factor = excluded.pass_factor,
            gold_mizer_factor = excluded.gold_mizer_factor,
            dark_notrump_factor = excluded.dark_notrump_factor,
            brow_factor = excluded.brow_factor,
            dark_mult = excluded.dark_mult,
            gold_mizer_on_null = excluded.gold_mizer_on_null,
            on_all_order = excluded.on_all_order,
            take_block_bonus = excluded.take_block_bonus,
            bet = excluded.bet,
            players_cnt = excluded.players_cnt,
            deal_types = excluded.deal_types,
            updated_at = current_timestamp
        """

        await db.execute(sql, game_id=game_id, **options.model_dump())

    @staticmethod
    async def add_player(game_id: int, player_id: UUID):
        sql = 'insert into game_players (game_id, player_id) values (%(game_id)s, %(player_id)s)'
        await db.execute(sql, game_id=game_id, player_id=player_id)

    @staticmethod
    async def del_player(game_id: int, player_id: UUID):
        sql = 'delete from game_players where game_id = %(game_id)s and player_id = %(player_id)s'
        await db.execute(sql, game_id=game_id, player_id=player_id)
