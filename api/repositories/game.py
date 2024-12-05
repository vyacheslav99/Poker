from datetime import datetime
from uuid import UUID

from api import db
from api.models.game import (GameCreateBody, GameModel, GameStatusEnum, Player, GameOptions, GameDateFilterFields,
                             GameSortFields)
from api.models.exceptions import NoChangesError


class GameRepo:

    @staticmethod
    async def create_game(owner_id: UUID, params: GameCreateBody) -> GameModel:
        sql = """
        insert into games (code, name, players_cnt, owner_id, status)
        values (%(code)s, %(name)s, %(players_cnt)s, %(owner_id)s, %(status)s)
        returning *
        """

        sql_add_player = """
        insert into game_players (game_id, player_id, fullname)
        select %(game_id)s, uid, fullname from users
        where uid = %(player_id)s
        """

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
                'uid', u.uid, 'username', u.username, 'fullname', coalesce(u.fullname, gp.fullname), 'avatar', u.avatar,
                'is_robot', coalesce(u.is_robot, false)
            )) as players
        from games g
            left join game_players gp on gp.game_id = g.id
            left join users u on u.uid = gp.player_id
        where g.id = %(game_id)s
        group by g.id
        """

        row = await db.fetchone(sql, game_id=game_id)
        return GameModel.make(dict(row)) if row else None

    @staticmethod
    async def get_games_list(
        game_ids: list[int] = None,
        code: str = None,
        name: str = None,
        owner_id: UUID | str = None,
        owner_name: str = None,
        statuses: list[GameStatusEnum] = None,
        date_from: datetime = None,
        date_to: datetime = None,
        date_field: GameDateFilterFields = None,
        sort_field: GameSortFields = None,
        sort_desc: bool = None,
        limit: int = None,
        offset: int = None
    ) -> tuple[int, list[GameModel]]:
        conditions = db.expressions.condition()

        if game_ids:
            conditions.and_x('g.id = any(%(game_ids)s)', game_ids=game_ids)
        if code:
            conditions.and_x('g.code = %(code)s', code=code)
        if name:
            conditions.and_x('lower(g.name) like %(name)s', name=f'%{name}%'.lower())
        if owner_id:
            conditions.and_x('g.owner_id = %(owner_id)s', owner_id=owner_id)
        if owner_name:
            cond = db.expressions.condition()
            cond.or_x('lower(u.username) like %(username)s', username=f'%{owner_name}%'.lower())
            cond.or_x('lower(u.fullname) like %(fullname)s', fullname=f'%{owner_name}%'.lower())
            conditions.and_x(cond, **cond.values)
        if statuses:
            conditions.and_x('g.status = any(%(statuses)s)', statuses=statuses)
        if date_from and date_field:
            conditions.and_x(f'g.{date_field} >= %(date_from)s', date_from=date_from)
        if date_to and date_field:
            conditions.and_x(f'g.{date_field} <= %(date_to)s', date_to=date_to)

        if sort_field:
            if sort_field == GameSortFields.owner_name:
                sort_field = 'u.fullname'
            else:
                sort_field = f'g.{sort_field}'

            order_str = f"order by {sort_field} {'desc' if sort_desc else ''}"
        else:
            order_str = ''

        limit_str = f'limit {limit}' if limit is not None else ''
        offset_str = f'offset {offset}' if offset is not None else ''

        sql = f"""
        select g.id, null as code, g.name, g.players_cnt, g.owner_id, g.status, g.created_at, g.started_at, g.paused_at,
            g.resumed_at, g.finished_at,
            jsonb_agg(json_build_object(
                'uid', u.uid, 'username', u.username, 'fullname', coalesce(u.fullname, gp.fullname), 'avatar', u.avatar,
                'is_robot', coalesce(u.is_robot, false)
            )) as players
        from games g
            left join game_players gp on gp.game_id = g.id
            left join users u on u.uid = gp.player_id
        where {conditions}
        group by g.id
        """

        sql_total = f'select count(*) from ({sql}) as q'
        sql = f'{sql} {order_str} {limit_str} {offset_str}'

        total = await db.fetchval(sql_total, **conditions.values)
        data = await db.fetchall(sql, **conditions.values)

        return total, [GameModel.make(dict(row)) for row in data]

    @staticmethod
    async def get_game_players(game_id: int) -> list[Player]:
        sql = """
        select u.uid, u.username, coalesce(u.fullname, gp.fullname) as fullname, u.avatar,
            coalesce(u.is_robot, false) as is_robot
        from game_players gp
            left join users u on u.uid = gp.player_id
        where gp.game_id = %(game_id)s
        """

        data = await db.fetchall(sql, game_id=game_id)
        return [Player(**row) for row in data]

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
    async def add_player(game_id: int, player_id: UUID, fullname: str):
        sql = """
        insert into game_players (game_id, player_id, fullname)
        values (%(game_id)s, %(player_id)s, %(fullname)s)
        """

        await db.execute(sql, game_id=game_id, player_id=player_id, fullname=fullname)

    @staticmethod
    async def del_player(game_id: int, player_id: UUID):
        sql = 'delete from game_players where game_id = %(game_id)s and player_id = %(player_id)s'
        await db.execute(sql, game_id=game_id, player_id=player_id)
