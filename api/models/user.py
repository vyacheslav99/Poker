from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from api.models.model import ModelMixin


class UserPublic(BaseModel):
    uid: UUID
    username: str
    fullname: str
    avatar: str | None = None
    is_robot: bool = False


class User(UserPublic):
    password: str
    disabled: bool = False
    curr_sid: UUID | None = None
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


class DeleteUserBody(BaseModel):
    password: str


class ClientParams(BaseModel, ModelMixin):

    _json_fields = {'custom_decoration'}

    color_theme: str
    style: str
    deck_type: str
    back_type: int
    sort_order: int
    lear_order: list[int]
    start_type: int
    custom_decoration: dict
    show_bikes: bool
