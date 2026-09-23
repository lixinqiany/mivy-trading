"""Asynchronous PostgreSQL client."""

from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import PostgresConfig
from .pool import PostgresPoolOptions


class AsyncPostgresClient:
    """Own a lazy async engine for use within one event loop.

    Each task needs its own connection or session. Await dispose() before loop exit.
    """

    def __init__(
        self,
        config: PostgresConfig,
        *,
        pool_options: PostgresPoolOptions | None = None,
    ) -> None:
        options = pool_options if pool_options is not None else PostgresPoolOptions()
        self._engine = create_async_engine(config.url, **options.asdict())
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def connect(self) -> AsyncConnection:
        """Return a connection for ``async with``; do not await this method.

        No automatic commit. Context exit rolls back uncommitted work and
        releases the connection.
        """
        return self._engine.connect()

    def begin(self) -> AbstractAsyncContextManager[AsyncConnection]:
        """Commit on success or roll back on error, then release the connection.

        Use ``async with client.begin()`` without awaiting this method.
        """
        return self._engine.begin()

    def session(self) -> AsyncSession:
        """Create a session for ``async with``; do not await this method.

        Exit closes the session and rolls back uncommitted work. No automatic
        commit. Each concurrent task needs its own session.
        """
        return self._session_factory()

    def session_begin(self) -> AbstractAsyncContextManager[AsyncSession]:
        """Create a session; commit on success or roll back on error, then close.

        Use ``async with client.session_begin()`` without awaiting this method.
        Exceptions propagate to the caller.
        """
        return self._session_factory.begin()

    async def dispose(self) -> None:
        """Dispose the pool; close sessions and release connections first.

        Borrowed connections stay open. The engine can create a new pool later.
        """
        await self._engine.dispose()
