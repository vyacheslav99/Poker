import re
import typing
import asyncpg

from collections import defaultdict
from asyncpg.cursor import CursorFactory
from asyncpg.pool import Pool
from asyncpg.transaction import Transaction

_K = typing.TypeVar('_K')

if typing.TYPE_CHECKING:
    _MutableMapping = typing.MutableMapping[_K, int]


class HitCount(typing.MutableMapping, typing.Generic[_K]):
    """
    Helper class to find parameters that are present in the string interpolation statement
    Acts like collections.defaultdict(int) but increases the number on the __getitem__() call
    String example:
        What a $(stmt)s day, $(name)s!

    get_used result:
        [stmt, name]
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        self.counter: dict[_K, int] = defaultdict(int)

    def __getitem__(self, key: _K) -> int:
        self.counter[key] += 1
        return self.counter[key]

    def __setitem__(self, key: _K, value: int) -> None:
        self.counter[key] = value

    def __delitem__(self, key: _K) -> None:
        self.counter[key] = 0

    def __iter__(self) -> typing.Iterator[_K]:
        return iter(self.counter)

    def __len__(self) -> int:
        return len(self.counter)

    def get_used(self) -> list[_K]:
        return [k for k, v in self.counter.items() if v > 0]


class ConnectionProxy:

    def __init__(self, pool: Pool):
        self._pool = pool
        self._conn: asyncpg.Connection | None = None

    def transaction(self) -> Transaction:
        assert self._conn, 'connection not acquired, use context manager'
        return self._conn.transaction(isolation='read_committed', readonly=False, deferrable=False)

    def fetchall(self, query: str, *args: typing.Any, **kwargs: typing.Any) -> typing.Awaitable[list]:
        query, values = self._make_native_placeholders(query, *args, **kwargs)
        return typing.cast(
            typing.Awaitable[typing.List[asyncpg.Record]],
            (self._conn or self._pool).fetch(query, *values)
        )

    def fetchone(
        self, query: str, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Awaitable[typing.Optional[asyncpg.Record]]:
        query, values = self._make_native_placeholders(query, *args, **kwargs)
        return typing.cast(
            typing.Awaitable[typing.Optional[asyncpg.Record]],
            (self._conn or self._pool).fetchrow(query, *values)
        )

    def fetchval(self, query: str, *args: typing.Any, **kwargs: typing.Any) -> typing.Awaitable[typing.Any]:
        query, values = self._make_native_placeholders(query, *args, **kwargs)
        return typing.cast(typing.Awaitable[typing.Any], (self._conn or self._pool).fetchval(query, *values))

    def execute(self, query: str, *args: typing.Any, **kwargs: typing.Any) -> typing.Awaitable[str]:
        query, values = self._make_native_placeholders(query, *args, **kwargs)
        return typing.cast(typing.Awaitable[str], (self._conn or self._pool).execute(query, *values))

    def executemany(self, query: str, args: typing.Any) -> typing.Awaitable[str]:
        return typing.cast(typing.Awaitable[str], (self._conn or self._pool).executemany(query, args))

    def prepare(self, query: str, *, name: str | None = None):
        if not self._conn:
            raise ValueError("Connection is required to call prepare")
        return self._conn.prepare(query, name=name)

    def cursor(
        self, query: str, *args: typing.Any, prefetch: int | None = None, **kwargs: typing.Any
    ) -> CursorFactory:
        if not self._conn:
            raise ValueError("Connection is required to call :meth cursor")
        query, values = self._make_native_placeholders(query, *args, **kwargs)
        return self._conn.cursor(query, *values, prefetch=prefetch)

    async def __aenter__(self) -> 'ConnectionProxy':
        self._conn = await self._pool.acquire()
        return self

    async def __aexit__(self, exc_type: type, exc_val: typing.Any, exc_tb: typing.Any) -> None:
        await self._pool.release(self._conn)
        self._conn = None

    @classmethod
    def _make_native_placeholders(
        cls, query: str, *args: typing.Any, **kwargs: typing.Any
    ) -> tuple[str, typing.Iterable]:
        if 'values' in kwargs:
            return cls._make_values(query=query, values=kwargs['values'])

        used_params = {}

        if kwargs:
            hit_count: HitCount[str] = HitCount(**kwargs)
            query % hit_count
            used_params = {key: kwargs[key] for key in hit_count.get_used()}

        params = {key: f'${i}' for i, key in enumerate(used_params, start=len(args) + 1)}

        return query % params, (*args, *used_params.values())

    @staticmethod
    def _make_values(query: str, values: list[dict]) -> tuple[str, list[typing.Any]]:
        if not isinstance(values, list) or not values:
            raise ValueError(f'Expected list[dict] got {type(values)} instead; List should not be empty')

        hit_count: HitCount[str] = HitCount(**values[0])
        query % hit_count
        used_params = {key: values[0][key] for key in hit_count.get_used() if key in values[0]}

        params = {key: i + 1 for i, key in enumerate(used_params)}
        query_list = re.split("(?i)values\s*\((\s*%\([\w]*s*\)s|[\w]*,*\s*)*\)", query)
        value_part = []
        query_values: typing.List[typing.Any] = []

        for curr_idx, item in enumerate(values):
            placeholders = {}
            for key, value in params.items():
                placeholders[f'${curr_idx * len(used_params) + value}'] = item[key]

            value_part.append(
                f"{',' if len(query_values) > 0 else 'values'} {tuple(placeholders.keys())}".replace("'", "")
            )
            query_values.extend(placeholders.values())

        query_list[1] = ''.join(value_part)
        return ''.join(query_list), query_values
