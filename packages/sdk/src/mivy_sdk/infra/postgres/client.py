"""Synchronous PostgreSQL client."""

from contextlib import AbstractContextManager

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from .config import PostgresConfig
from .pool import PostgresPoolOptions


class PostgresClient:
    def __init__(
        self,
        config: PostgresConfig,
        *,
        pool_options: PostgresPoolOptions | None = None,
    ) -> None:
        options = pool_options if pool_options is not None else PostgresPoolOptions()
        self._engine = create_engine(config.url, **options.asdict())

    @property
    def engine(self) -> Engine:
        return self._engine

    def connect(self) -> Connection:
        """Acquire a connection for ``with``; no automatic commit.

        Context exit rolls back uncommitted work and releases the connection.
        """
        return self._engine.connect()

    def begin(self) -> AbstractContextManager[Connection]:
        """Commit on success or roll back on error, then release the connection.

        Use as ``with client.begin() as connection:``.
        """
        return self._engine.begin()

    def dispose(self) -> None:
        """Dispose the pool; release borrowed connections before calling.

        Borrowed connections stay open. The engine can create a new pool later.
        """
        self._engine.dispose()
