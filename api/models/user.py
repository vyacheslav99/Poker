import uuid

from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel


class UserPublic(BaseModel):
    uid: uuid.UUID
    username: str
    fullname: str
    avatar: str | None = None


class User(UserPublic):
    password: str
    disabled: bool = False
    curr_sid: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChangePasswordBody(BaseModel):
    password: str
    new_password: str
    close_sessions: bool = False


class ChangeUsernameBody(BaseModel):
    new_username: str


class UserPatchBody(BaseModel):
    fullname: str | None = None


class DeleteUserBody(BaseModel):
    password: str


class ClientParams(BaseModel):
    color_theme: str
    style: str
    deck_type: str
    back_type: int
    sort_order: int
    lear_order: list[int]
    start_type: int
    custom_decoration: dict
    show_bikes: bool


class GameOptions(BaseModel):
    game_sum_by_diff: bool
    dark_allowed: bool
    third_pass_limit: bool
    fail_subtract_all: bool
    no_joker: bool
    joker_give_at_par: bool
    joker_demand_peak: bool
    pass_factor: int
    gold_mizer_factor: int
    dark_notrump_factor: int
    brow_factor: int
    dark_mult: int
    gold_mizer_on_null: bool
    on_all_order: bool
    take_block_bonus: bool
    bet: int
    players_cnt: int
    deal_types: list[int]


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
    uid: uuid.UUID
    name: str
    avatar: str | None = None
    is_robot: bool = False


class OverallStatisticsResponse(BaseModel):
    items: list[UserStatistics]
    total: int
