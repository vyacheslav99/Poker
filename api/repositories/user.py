from uuid import UUID
from api import db
from api.db.expressions import condition
from api.models.user import User, ClientParams, GameOptions, StatisticsItem, UserStatistics
from api.models.security import Session
from api.models.exceptions import NoChangesError


class UserRepo:

    _protected_user_fileds = ['uid']

    @staticmethod
    async def get_user(user_id: UUID | str = None, username: str = None) -> User | None:
        if not user_id and not username:
            raise Exception('Один из параметров должен быть передан: user_id or username')

        conditions = db.expressions.condition()

        if user_id:
            conditions.and_x('uid = %(uid)s', uid=user_id)
        if username:
            conditions.and_x('username = %(username)s', username=username)

        row = await db.fetchone(f'select * from users where {conditions}', **conditions.values)
        return User(**row) if row else None

    @staticmethod
    async def create_user(user: User) -> User:
        sql = """
        insert into users (uid, username, fullname, password)
        values (%(uid)s, %(username)s, %(fullname)s, %(password)s)
        returning *
        """

        res = await db.fetchone(sql, **user.model_dump())
        return User(**res) if res else None

    @staticmethod
    async def update_user(user_id: UUID, **data) -> User:
        fields = db.expressions.set()

        for k, v in data.items():
            if k not in UserRepo._protected_user_fileds:
                fields.field(k, v)

        if not fields.values:
            raise NoChangesError('Nothing to change')

        sql = f"""
        update users set
            updated_at = current_timestamp,
            {fields}
        where uid = %(uid)s
        returning *
        """

        row = await db.fetchone(sql, uid=user_id, **fields.values)
        return User(**row) if row else None

    @staticmethod
    async def delete_user(user_id: UUID):
        await db.execute('delete from users where uid = %(uid)s', uid=user_id)

    @staticmethod
    async def get_session(session_id: UUID) -> Session | None:
        sql = """
        select s.*, u.username
        from session s
            join users u on u.uid = s.uid
        where s.sid = %(sid)s
        """

        row = await db.fetchone(sql, sid=session_id)
        return Session.make(dict(row)) if row else None

    @staticmethod
    async def get_user_sessions(user_id: UUID) -> list[Session]:
        sql = """
        select s.*, u.username
        from session s
            join users u on u.uid = s.uid
        where s.uid = %(uid)s
        """

        data = await db.fetchall(sql, uid=user_id)
        return [Session.make(dict(row)) for row in data]

    @staticmethod
    async def create_session(session: Session):
        sql = """
        insert into session (sid, uid, client_info)
        values (%(sid)s, %(uid)s, %(client_info)s)
        """

        await db.execute(sql, **session.dump())

    @staticmethod
    async def delete_sessions(session_ids: list[UUID]):
        await db.execute('delete from session where sid = any(%(session_ids)s)', session_ids=session_ids)

    @staticmethod
    async def get_user_params(user_id: UUID) -> ClientParams | None:
        sql = 'select * from user_params where uid = %(uid)s'

        row = await db.fetchone(sql, uid=user_id)
        return ClientParams.make(dict(row)) if row else None

    @staticmethod
    async def set_user_params(user_id: UUID, params: ClientParams):
        sql = """
        insert into user_params (uid, color_theme, style, deck_type, back_type, sort_order, lear_order, start_type,
            custom_decoration, show_bikes)
        values (%(uid)s, %(color_theme)s, %(style)s, %(deck_type)s, %(back_type)s, %(sort_order)s, %(lear_order)s,
            %(start_type)s, %(custom_decoration)s, %(show_bikes)s)
        on conflict on constraint user_params_pk do update set
            color_theme = excluded.color_theme,
            style = excluded.style,
            deck_type = excluded.deck_type,
            back_type = excluded.back_type,
            sort_order = excluded.sort_order,
            lear_order = excluded.lear_order,
            start_type = excluded.start_type,
            custom_decoration = excluded.custom_decoration,
            show_bikes = excluded.show_bikes,
            updated_at = current_timestamp
        """

        await db.execute(sql, uid=user_id, **params.dump())

    @staticmethod
    async def get_user_game_options(user_id: UUID) -> GameOptions | None:
        sql = 'select * from user_game_options where uid = %(uid)s'

        row = await db.fetchone(sql, uid=user_id)
        return GameOptions(**row) if row else None

    @staticmethod
    async def set_user_game_options(user_id: UUID, options: GameOptions):
        sql = """
        insert into user_game_options (uid, game_sum_by_diff, dark_allowed, third_pass_limit, fail_subtract_all,
            no_joker, joker_give_at_par, joker_demand_peak, pass_factor, gold_mizer_factor, dark_notrump_factor,
            brow_factor, dark_mult, gold_mizer_on_null, on_all_order, take_block_bonus, bet, players_cnt, deal_types)
        values (%(uid)s, %(game_sum_by_diff)s, %(dark_allowed)s, %(third_pass_limit)s, %(fail_subtract_all)s,
            %(no_joker)s, %(joker_give_at_par)s, %(joker_demand_peak)s, %(pass_factor)s, %(gold_mizer_factor)s,
            %(dark_notrump_factor)s, %(brow_factor)s, %(dark_mult)s, %(gold_mizer_on_null)s, %(on_all_order)s,
            %(take_block_bonus)s, %(bet)s, %(players_cnt)s, %(deal_types)s)
        on conflict on constraint user_game_options_pk do update set
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

        await db.execute(sql, uid=user_id, **options.model_dump())

    @staticmethod
    async def get_statistics(
        include_user_ids: list[UUID] = None, sort_field: str = 'summary', sord_desc: bool = True, limit: int = 20
    ) -> list[UserStatistics]:
        sql = f"""
        with stat1 as (
            select s.uid, u.fullname as name, u.avatar, false as is_robot, s.started, s.completed, s.thrown, s.winned,
                s.lost, s.summary, s.total_money, s.last_scores, s.last_money, s.best_scores, s.best_money,
                s.worse_scores, s.worse_money
            from statistics s
                join users u on u.uid = s.uid
            where s.uid = any(%(uids)s)
        ),
        stat2 as (
            select s.uid, u.fullname as name, u.avatar, false as is_robot, s.started, s.completed, s.thrown, s.winned,
                s.lost, s.summary, s.total_money, s.last_scores, s.last_money, s.best_scores, s.best_money,
                s.worse_scores, s.worse_money
            from statistics s
                join users u on u.uid = s.uid
            where not u.disabled
            order by {sort_field} {'desc' if sord_desc else 'asc'}
            limit {limit or 20}
        )
        select * from stat1
        union
        select * from stat2
        order by {sort_field} {'desc' if sord_desc else 'asc'}
        """

        data = await db.fetchall(sql, uids=include_user_ids or [])
        return [UserStatistics(**row) for row in data]

    @staticmethod
    async def set_user_statistics(user_id: UUID, item: StatisticsItem):
        sql = """
        insert into statistics (uid, started, completed, thrown, winned, lost, summary, total_money, last_scores,
            last_money, best_scores, best_money, worse_scores, worse_money)
        values (%(uid)s, %(started)s, %(completed)s, %(thrown)s, %(winned)s, %(lost)s, %(summary)s, %(total_money)s,
            %(last_scores)s, %(last_money)s, %(best_scores)s, %(best_money)s, %(worse_scores)s, %(worse_money)s)
        on conflict on constraint statistics_pk do update set
            started = excluded.started,
            completed = excluded.completed,
            thrown = excluded.thrown,
            winned = excluded.winned,
            lost = excluded.lost,
            summary = excluded.summary,
            total_money = excluded.total_money,
            last_scores = excluded.last_scores,
            last_money = excluded.last_money,
            best_scores = excluded.best_scores,
            best_money = excluded.best_money,
            worse_scores = excluded.worse_scores,
            worse_money = excluded.worse_money,
            updated_at = current_timestamp
        """

        await db.execute(sql, uid=user_id, **item.model_dump())
