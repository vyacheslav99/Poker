""" Адаптеры для работы с БД """

import sqlite3


def dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


class sqlite_connection(object):

    def __init__(self, database, **kwargs):
        self._db_con = sqlite3.connect(database, **kwargs)
        self._db_con.row_factory = dict_factory

    def get_connect(self):
        return self._db_con

    def cursor(self):
        return self._db_con.cursor()

    def execute(self, sql, params, commit=False):
        cur = self._db_con.cursor()
        cur.execute(sql, params)

        if commit:
            self._db_con.commit()

        return cur

    def commit(self):
        self._db_con.commit()

    def rollback(self):
        self._db_con.rollback()
