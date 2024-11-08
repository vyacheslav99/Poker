import uuid

from datetime import datetime
from pydantic import BaseModel


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


class ChangePasswordBody(BaseModel):
    password: str
    new_password: str
    close_sessions: bool = False


class ChangeUsernameBody(BaseModel):
    new_username: str


class UserPatchBody(BaseModel):
    fullname: str | None = None
