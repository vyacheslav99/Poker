import uuid

from datetime import datetime
from pydantic import BaseModel

from api.models.model import ModelMixin


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sid: str
    sub: str
    exp: int


class LoginBody(BaseModel):
    username: str
    password: str


class Session(BaseModel, ModelMixin):

    _json_fields = {'client_info'}

    sid: uuid.UUID
    uid: uuid.UUID
    username: str | None = None
    client_info: dict | None = None
    created_at: datetime | None = None
    is_current: bool = False
