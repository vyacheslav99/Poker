"""
init migration
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.users
(
    uid        uuid        not null
        constraint users_pk
            primary key,
    username   varchar(64) not null
        constraint users_ux_username
            unique,
    fullname   varchar     not null,
    password   varchar     not null,
    avatar     varchar,
    disabled   bool        default false,
    created_at timestamptz default current_timestamp,
    updated_at timestamptz
);
    """)
]
