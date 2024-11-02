import asyncio
import collections
import typing
import asyncpg

from .connection import ConnectionProxy
from .expressions.condition import ConditionExpression

POOL_DEFAULT_NAME = 'default'
POOLS_REGISTRY: dict[str, asyncpg.pool.Pool] = {}
POOLS_REGISTRY_PARTY: dict[str, int] = collections.Counter()
POOLS_REGISTRY_WAITERS: dict[str, list[asyncio.Future]] = collections.defaultdict(list)


async def setup(settings: typing.Dict[str, dict]) -> None:
    loop = asyncio.get_running_loop()

    for dbname, options in settings.items():
        if POOLS_REGISTRY_PARTY[dbname] > 0:
            _pool_init_waiter = loop.create_future()
            POOLS_REGISTRY_PARTY[dbname] += 1
            POOLS_REGISTRY_WAITERS[dbname].append(_pool_init_waiter)
            return await _pool_init_waiter

        options = {**options}
        POOLS_REGISTRY_PARTY[dbname] += 1
        POOLS_REGISTRY[dbname] = await asyncpg.create_pool(
            dsn=options.pop('dsn'),
            min_size=options.pop('min_size'),
            max_size=options.pop('max_size'),
            connection_class=asyncpg.Connection,
            **options
        )

        waiters = POOLS_REGISTRY_WAITERS[dbname]
        POOLS_REGISTRY_WAITERS[dbname] = []

        for waiter in waiters:
            if not waiter.done():
                waiter.set_result(None)


async def shutdown() -> None:
    for dbname, pool in POOLS_REGISTRY.items():
        POOLS_REGISTRY_PARTY[dbname] -= 1
        if POOLS_REGISTRY_PARTY[dbname] < 1:
            await pool.close()


def connection(dbname: str = POOL_DEFAULT_NAME) -> ConnectionProxy:
    return ConnectionProxy(POOLS_REGISTRY[dbname])


def fetchall(
    query: str, *args: typing.Any, dbname: str = POOL_DEFAULT_NAME, **kwargs: typing.Any
) -> typing.Awaitable[list]:
    return connection(dbname).fetchall(query, *args, **kwargs)


def fetchone(
    query: str, *args: typing.Any, dbname: str = POOL_DEFAULT_NAME, **kwargs: typing.Any
) -> typing.Awaitable[typing.Optional[asyncpg.Record]]:
    return connection(dbname).fetchone(query, *args, **kwargs)


def fetchval(
    query: str, *args: typing.Any, dbname: str = POOL_DEFAULT_NAME, **kwargs: typing.Any
) -> typing.Awaitable[typing.Any]:
    return connection(dbname).fetchval(query, *args, **kwargs)


def execute(
    query: str, *args: typing.Any, dbname: str = POOL_DEFAULT_NAME, **kwargs: typing.Any
) -> typing.Awaitable[str]:
    return connection(dbname).execute(query, *args, **kwargs)


def executemany(query: str, args: typing.Any, *, dbname: str = POOL_DEFAULT_NAME) -> typing.Awaitable[str]:
    return connection(dbname).executemany(query, args)
