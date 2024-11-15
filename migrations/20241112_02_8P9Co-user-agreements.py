"""
user agreements
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.user_game_options
(
    uid                 uuid   not null
        constraint user_game_options_pk primary key
        constraint user_game_options_user_fk
            references public.users
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
    created_at          timestamptz default current_timestamp,
    updated_at          timestamptz
);
    """)
]
