import uuid

from datetime import datetime
from pydantic import BaseModel, Field

from api.models.model import ModelMixin


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sid: str
    sub: str
    exp: int


class LoginBody(BaseModel):
    username: str = Field(min_length=3,
                          description='Может содержать только буквы английского алфавита, цифры и спец символы')
    password: str = Field(description='Значение должно быть зашифровано и закодировано в base64')


class Session(BaseModel, ModelMixin):

    _json_fields = {'client_info'}

    sid: uuid.UUID
    uid: uuid.UUID
    username: str | None = None
    client_info: dict | None = None
    created_at: datetime | None = None
    is_current: bool = False
