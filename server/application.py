from typing import Optional

from server.db import postgresql_connection


class Application:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Application, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self._db: Optional[postgresql_connection] = None

    @property
    def db(self) -> postgresql_connection:
        return self._db

    @db.setter
    def db(self, conn: postgresql_connection):
        self._db = conn


app = Application()