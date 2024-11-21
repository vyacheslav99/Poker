"""
user statistics
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.statistics
(
    uid          uuid not null
        constraint statistics_pk
            primary key
        constraint statistics_users_fk
            references public.users
            on update cascade on delete cascade,
    started      integer          default 0,
    completed    integer          default 0,
    thrown       integer          default 0,
    winned       integer          default 0,
    lost         integer          default 0,
    summary      integer          default 0,
    total_money  double precision default 0.0,
    last_scores  integer          default 0,
    last_money   double precision default 0.0,
    best_scores  integer          default 0,
    best_money   double precision default 0.0,
    worse_scores integer          default 0,
    worse_money  double precision default 0.0,
    created_at timestamptz default current_timestamp,
    updated_at timestamptz
);
    """),

    step("""
insert into statistics (uid)
select uid from users;
    """)
]
