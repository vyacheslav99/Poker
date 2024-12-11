from uuid import UUID
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field

from api.models.model import ModelMixin


class GameStatusEnum(StrEnum):
    # Черновик. Владелец настраивает кол-во игроков, договоренности, может поменять код и название.
    # Видит только владелец.
    DRAFT = 'draft'
    # Ожидание игроков. Этап присоединения игроков. Видят все
    WAITING = 'waiting'
    # Игра начата
    STARTED = 'started'
    # Пауза (приостановлена)
    PAUSED = 'paused'
    # Игра завершена (доиграна до конца)
    FINISHED = 'finished'
    # Игра брошена (один или несколько игроков покинули игру и не стали доигрывать)
    ABORTED = 'aborted'

    @classmethod
    def editing_statuses(cls) -> set["GameStatusEnum"]:
        return {cls.DRAFT, cls.WAITING}

    @classmethod
    def playing_statuses(cls) -> set["GameStatusEnum"]:
        return {cls.STARTED, cls.PAUSED}

    @classmethod
    def finished_statuses(cls) -> set["GameStatusEnum"]:
        return {cls.FINISHED, cls.ABORTED}

    @classmethod
    def status_transitions(cls) -> dict["GameStatusEnum", set["GameStatusEnum"]]:
        """
        Вернет словарь с какого на какой статус можно перейти: ключ - статус С которого переходим, значение -
        список статусов НА которые можно перейти
        """

        return {
            cls.DRAFT: {cls.WAITING},
            cls.WAITING: {cls.STARTED},
            cls.STARTED: {cls.PAUSED, cls.FINISHED, cls.ABORTED},
            cls.PAUSED: {cls.STARTED, cls.ABORTED},
            cls.FINISHED: set(),
            cls.ABORTED: set()
        }

    def allow_pass_to(self, new_status: "GameStatusEnum") -> bool:
        """ Возможно ли перейти с текущего статуса (экземпляра enum-а) на переданный """

        return new_status in self.status_transitions()[self]


class Player(BaseModel):
    uid: UUID | None = None
    username: str | None = None
    fullname: str | None = None
    avatar: str | None = None
    is_robot: bool = False
    risk_level: int | None = None


class GameModel(BaseModel, ModelMixin):

    _json_fields = {'players'}

    id: int
    code: str | None
    name: str
    owner_id: UUID
    status: GameStatusEnum
    players_cnt: int
    players: list[Player]
    created_at: datetime
    started_at: datetime | None = None
    paused_at: datetime | None = None
    resumed_at: datetime | None = None
    finished_at: datetime | None = None

    def allow_edit(self) -> bool:
        return self.status in GameStatusEnum.editing_statuses()


class GameCreateBody(BaseModel):
    code: str | None = Field(min_length=1)
    name: str = Field(min_length=3)
    players_cnt: int = Field(ge=3, le=4)


class GamePatchBody(BaseModel):
    code: str = Field(min_length=1, default=None)
    name: str = Field(min_length=3, default=None)
    players_cnt: int = Field(ge=3, le=4, default=None)


class SetGameStatusBody(BaseModel):
    status: GameStatusEnum


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


class GameDateFilterFields(StrEnum):
    created_at = 'created_at'
    started_at = 'started_at'
    finished_at = 'finished_at'


class GameSortFields(StrEnum):
    game_id = 'id'
    created_at = 'created_at'
    started_at = 'started_at'
    finished_at = 'finished_at'
    game_name = 'name'
    owner_name = 'owner_name'


class GamesListResponse(BaseModel):
    items: list[GameModel]
    total: int
    limit: int
    page: int
    skip: int


class JoinToGameBody(BaseModel):
    code: str | None = Field(min_length=1)
