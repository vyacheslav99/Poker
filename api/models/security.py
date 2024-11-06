import uuid

from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sid: str
    sub: str
    exp: int


class AuthBody(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    uid: uuid.UUID
    username: str
    fullname: str
    avatar: str | None = None


class User(UserBase):
    password: str
    disabled: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Session(BaseModel):
    sid: uuid.UUID
    uid: uuid.UUID
    username: str | None = None
    client_info: dict | None = None
    created_at: datetime | None = None


class ChangePasswordBody(BaseModel):
    password: str
    new_password: str
