"""
games
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.games
(
    id          serial                                not null
        constraint games_pk
            primary key,
    code        varchar                               not null,
    name        varchar                               not null,
    players_cnt integer                               not null,
    owner_id    uuid                                  not null
        constraint games_users_uid_fk
            references public.users
            on update cascade on delete cascade,
    status      varchar(32)                           not null,
    created_at  timestamptz default current_timestamp not null,
    started_at  timestamptz,
    paused_at   timestamptz,
    resumed_at  timestamptz,
    finished_at timestamptz
);

create index games_owner_id_idx
    on public.games (owner_id);

create index games_status_idx
    on public.games (status);    
    """),

    step("""
create table public.game_players
(
    id         serial                                not null
        constraint game_players_pk
            primary key,
    game_id    integer                               not null
        constraint game_players_games_id_fk
            references public.games
            on update cascade on delete cascade,
    player_id  uuid
        constraint game_players_users_uid_fk
            references public.users
            on update cascade on delete set null,
    fullname   varchar,
    risk_level integer,
    scores     integer,
    money      double precision,
    is_winner  boolean     default false,
    created_at timestamptz default current_timestamp not null
);

create index game_players_game_id_idx
    on public.game_players (game_id);

create index game_players_player_id_idx
    on public.game_players (player_id);
    """),

    step("""
create table game_options
(
    game_id                 serial not null
        constraint game_options_pk
            primary key
        constraint game_options_game_id_fk
            references games
            on update cascade on delete cascade,
    game_sum_by_diff    boolean,
    dark_allowed        boolean,
    third_pass_limit    boolean,
    fail_subtract_all   boolean,
    no_joker            boolean,
    joker_give_at_par   boolean,
    joker_demand_peak   boolean,
    pass_factor         integer,
    gold_mizer_factor   integer,
    dark_notrump_factor integer,
    brow_factor         integer,
    dark_mult           integer,
    gold_mizer_on_null  boolean,
    on_all_order        boolean,
    take_block_bonus    boolean,
    bet                 integer,
    players_cnt         integer,
    deal_types          integer[],
    created_at          timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at          timestamp with time zone
);
    """),

    step("""
alter table public.users
    add is_robot boolean not null default false;

create index users_robot_idx
    on public.users (is_robot);
    """)
]
