from uuid import UUID
from enum import StrEnum
from pydantic import BaseModel


class StatisticsSortFields(StrEnum):
    started = 'started'
    completed = 'completed'
    thrown = 'thrown'
    winned = 'winned'
    lost = 'lost'
    summary = 'summary'
    total_money = 'total_money'
    last_scores = 'last_scores'
    last_money = 'last_money'
    best_scores = 'best_scores'
    best_money = 'best_money'
    worse_scores = 'worse_scores'
    worse_money = 'worse_money'


class StatisticsItem(BaseModel):
    started: int = 0            # кол-во начатых игр (+1 в начале игры)
    completed: int = 0          # кол-во сыгранных игр (+1 при завершении игры)
    thrown: int = 0             # кол-во брошенных партий (+1 когда бросаешь игру)
    winned: int = 0             # кол-во выигранных партий (+1 при выигрыше (набрал больше всех))
    lost: int = 0               # кол-во проигранных партий (+1 при проигрыше)
    summary: int = 0            # общий суммарный выигрыш (сумма очков всех сыгранных партий)
    total_money: float = 0.0    # общая сумма денег (сумма денег всех сыгранных партий)
    last_scores: int = 0        # последний выигрыш (очки)
    last_money: float = 0.0     # последний выигрыш (деньги)
    best_scores: int = 0        # лучший выигрыш (очки)
    best_money: float = 0.0     # лучший выигрыш (деньги)
    worse_scores: int = 0       # худший результат (очки)
    worse_money: float = 0.0    # худший результат (деньги)


class UserStatistics(StatisticsItem):
    uid: UUID
    name: str
    is_robot: bool
    avatar: str | None = None


class OverallStatisticsResponse(BaseModel):
    items: list[UserStatistics]
    total: int
