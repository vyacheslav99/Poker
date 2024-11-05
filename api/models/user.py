import uuid

from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthData(BaseModel):
    username: str
    password: str


class User(BaseModel):
    uid: uuid.UUID
    username: str
    fullname: str
    avatar: str | None = None


class UserDTO(User):
    password: str
    disabled: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
