from uuid import UUID

from api import db
from api.models.statistics import UserStatistics


class MiscRepo:

    @staticmethod
    async def get_statistics(
        include_user_ids: list[UUID] = None, sort_field: str = 'summary', sord_desc: bool = True, limit: int = 20
    ) -> list[UserStatistics]:
        sql = f"""
        with stat1 as (
            select s.uid, u.fullname as name, u.avatar, u.is_robot, s.started, s.completed, s.thrown, s.winned,
                s.lost, s.summary, s.total_money, s.last_scores, s.last_money, s.best_scores, s.best_money,
                s.worse_scores, s.worse_money
            from statistics s
                join users u on u.uid = s.uid
            where s.uid = any(%(uids)s)
        ),
        stat2 as (
            select s.uid, u.fullname as name, u.avatar, u.is_robot, s.started, s.completed, s.thrown, s.winned,
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
