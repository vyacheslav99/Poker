"""
robots
"""

from yoyo import step

__depends__ = {}


def _get_sql():
    from uuid import uuid4
    from gui.common.const import ROBOTS
    from gui.common.utils import gen_passwd

    values = []

    for name in ROBOTS:
        values.append(f"('{uuid4()}', '{gen_passwd(6)}', '{name}', '{gen_passwd(6)}', true)")

    return f"insert into users (uid, username, fullname, password, is_robot) values\n{',\n'.join(values)}"


steps = [
    step(_get_sql())
]
