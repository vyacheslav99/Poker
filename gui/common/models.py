import uuid
from datetime import datetime

from models.base_model import BaseModel
from models.player import Player


class Session(BaseModel):

    def __init__(self, **kwargs):
        self.sid: uuid.UUID | None = None
        self.uid: uuid.UUID | None = None
        self.username: str | None = None
        self.client_info: dict | None = None
        self.created_at: datetime | None = None
        self.is_current: bool = False

        super().__init__(**kwargs)


class GameModel(BaseModel):

    def __init__(self, **kwargs):
        self.id: int | None = None
        self.code: str | None = None
        self.name: str | None = None
        self.owner_id: uuid.UUID | None = None
        self.status: str | None = None
        self.players_cnt: int | None = None
        self.players: list[Player] | None = None
        self.created_at: datetime | None = None
        self.started_at: datetime | None = None
        self.paused_at: datetime | None = None
        self.resumed_at: datetime | None = None
        self.finished_at: datetime | None = None

        if 'players' in kwargs:
            kwargs['players'] = [Player(**kwargs['players'])]

        super().__init__(**kwargs)
