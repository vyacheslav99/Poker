import uuid

from datetime import datetime
from pydantic import BaseModel


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


class Session(BaseModel):
    sid: uuid.UUID
    uid: uuid.UUID
    username: str | None = None
    client_info: dict | None = None
    created_at: datetime | None = None
    is_current: bool = False


class ChangePasswordBody(BaseModel):
    password: str
    new_password: str
    close_sessions: bool = False


class ChangeUsernameBody(BaseModel):
    new_username: str
