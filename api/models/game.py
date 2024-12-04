from uuid import UUID
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field

from api.models.model import ModelMixin
from api.models.user import UserPublic


class GameStatusEnum(StrEnum):
    # Черновик. Владелец настраивает кол-во игроков, договоренности, может поменять код и название.
    # Видит только владелец.
    DRAFT = 'draft'
    # Ожидание игроков. Этап присоединения игроков. Видят все
    WAITING = 'waiting'
    # Готова к старту. Игра настроена и готова к старту, все игроки присоединились. Видят только участники
    READY = 'ready'
    # Игра начата
    STARTED = 'started'
    # Пауза (приостановлена)
    PAUSED = 'paused'
    # Игра завершена (доиграна до конца)
    FINISHED = 'finished'
    # Игра брошена (один или несколько игроков покинули игру и не стали доигрывать)
    ABORTED = 'aborted'


class GameCreateBody(BaseModel):
    code: str | None = Field(min_length=1)
    name: str = Field(min_length=3)
    players_cnt: int = Field(ge=3, le=4)


class GameModel(BaseModel, ModelMixin):

    _json_fields = {'players'}

    id: int
    code: str | None
    name: str
    owner_id: UUID
    status: GameStatusEnum
    players_cnt: int
    players: list[UserPublic]
    created_at: datetime
    started_at: datetime | None = None
    paused_at: datetime | None = None
    resumed_at: datetime | None = None
    finished_at: datetime | None = None


class GamePatchBody(BaseModel):
    code: str = Field(min_length=1, default=None)
    name: str = Field(min_length=3, default=None)
    players_cnt: int = Field(ge=3, le=4, default=None)


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


class PlayerAddBody(BaseModel):
    user_id: UUID = Field(default=None)
    username: str = Field(default=None)