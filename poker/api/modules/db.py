""" Адаптеры для работы с БД """

from typing import Union, Optional, List, Tuple, Dict
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor, RealDictConnection
from psycopg2 import DatabaseError, ProgrammingError


class postgresql_connection:

    def __init__(self, dbparams):
        dbparams['cursor_factory'] = RealDictCursor
        dbparams['maxconn'] = dbparams.get('maxconn', 10)
        self.__pool = ThreadedConnectionPool(minconn=1, **dbparams)

    def __get_conn__(self, key=None) -> RealDictConnection:
        con: RealDictConnection = self.__pool.getconn(key=key)
        if con.closed:
            self.__put_conn__(con, key=key)
            return self.__get_conn__(key=key)

        return con

    def __put_conn__(self, conn: RealDictConnection, key=None, close=False):
        self.__pool.putconn(conn, key=key, close=close)

    def __close_all(self):
        self.__pool.closeall()

    def close_connect(self, con: RealDictConnection, commit=True):
        if commit:
            con.commit()
        else:
            con.rollback()

        self.__put_conn__(con)

    def get_connect(self) -> RealDictConnection:
        return self.__get_conn__()

    def execute(self, query: str, params: Union[Tuple, Dict] = None, commit=True, con: Optional[RealDictConnection] = None,
                con_keep_open=False):
        """
        con: коннект, полученный методом get_connect для выполнения в пределах одной транзакции
        con_keep_open: True - оставлять коннект открытым (в этом случае параметр commit будет проигнорирован)
        для выполнения в одной транзакции нескольких запросов и ручной фиксации/отката транзакции.
        Если коннект не передан в метод извне, параметр игнорируется, а коннект будет закрыт
        """

        if not con:
            con_keep_open = False
            con = self.__get_conn__()

        cur: RealDictCursor = con.cursor()
        try:
            cur.execute(query, vars=params)
        except DatabaseError:
            self.close_connect(con, commit=False)
            raise

        try:
            res = cur.fetchall()
        except ProgrammingError:
            res = None

        cur.close()

        if not con_keep_open:
            self.close_connect(con, commit)

        return res[0] if res else None

    def fetchall(self, query: str, params: Union[Tuple, Dict] = None) -> List:
        con: RealDictConnection = self.__get_conn__()
        cur: RealDictCursor = con.cursor()

        try:
            cur.execute(query, vars=params)
        except DatabaseError:
            self.close_connect(con, commit=False)
            raise

        try:
            res = cur.fetchall()
        except ProgrammingError:
            res = []

        cur.close()
        self.close_connect(con)

        return res

    def fetchone(self, query: str, params: Union[Tuple, Dict] = None):
        con: RealDictConnection = self.__get_conn__()
        cur: RealDictCursor = con.cursor()

        try:
            cur.execute(query, vars=params)
        except DatabaseError:
            self.close_connect(con, commit=False)
            raise

        try:
            res = cur.fetchone()
        except ProgrammingError:
            res = None

        cur.close()
        self.close_connect(con)

        return res

    def fetchval(self, query: str, params: Union[Tuple, Dict] = None):
        row = self.fetchone(query, params=params)

        if row:
            if isinstance(row, tuple):
                return row[0]
            elif isinstance(row, dict):
                return row[tuple(row.keys())[0]]

        return None
