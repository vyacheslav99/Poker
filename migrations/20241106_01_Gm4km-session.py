"""
session
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
create table public.session
(
    sid uuid not null
        constraint session_pk primary key,
    uid uuid not null,
    client_info jsonb,
    created_at timestamp with time zone default CURRENT_TIMESTAMP
);

alter table public.session
    add constraint session_user_fk foreign key (uid) references public.users
        on update cascade on delete cascade;
        
create index session_uid_idx
    on session (uid);
    """)
]
