from uuid import UUID
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field

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


class GameModel(BaseModel):
    id: int
    code: str
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
