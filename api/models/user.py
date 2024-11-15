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


class DeleteUserBody(BaseModel):
    password: str


class ClientParams(BaseModel):
    color_theme: str
    style: str
    deck_type: str
    back_type: int
    sort_order: int
    lear_order: list[int]
    start_type: int
    custom_decoration: dict
    show_bikes: bool


class GameOptions(BaseModel):
    game_sum_by_diff: bool
    dark_allowed: bool
    third_pass_limit: bool
    fail_subtract_all: bool
    no_joker: bool
    joker_give_at_par: bool
    joker_demand_peak: bool
    pass_factor: int
    gold_mizer_factor: int
    dark_notrump_factor: int
    brow_factor: int
    dark_mult: int
    gold_mizer_on_null: bool
    on_all_order: bool
    take_block_bonus: bool
    bet: int
    players_cnt: int
    deal_types: list[int]
