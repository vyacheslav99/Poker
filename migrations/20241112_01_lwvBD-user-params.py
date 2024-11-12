"""
user params
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.user_params
(
    uid uuid not null
        constraint user_params_pk primary key 
        constraint user_params_user_fk references public.users
            on update cascade on delete cascade,
    color_theme varchar(32),
    style varchar(32),
    deck_type varchar(32),
    back_type integer,
    sort_order integer,
    lear_order integer[],
    start_type integer,
    custom_decoration jsonb,
    show_bikes boolean,
    created_at timestamptz default current_timestamp,
    updated_at timestamptz
);
    """)
]
