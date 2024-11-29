import uuid
from datetime import datetime

from models.base_model import BaseModel


class Session(BaseModel):

    def __init__(self, **kwargs):
        self.sid: uuid.UUID | None = None
        self.uid: uuid.UUID | None = None
        self.username: str | None = None
        self.client_info: dict | None = None
        self.created_at: datetime | None = None
        self.is_current: bool = False

        super().__init__(**kwargs)
