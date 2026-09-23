"""Synchronous PostgreSQL client."""

from contextlib import AbstractContextManager

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

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
        self._session_factory = sessionmaker(self._engine, expire_on_commit=False)

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

    def session(self) -> Session:
        """Create a session for ``with``; close on exit without automatic commit.

        Uncommitted work is rolled back. Each thread needs its own session.
        """
        return self._session_factory()

    def session_begin(self) -> AbstractContextManager[Session]:
        """Create a session; commit on success or roll back on error, then close.

        Use ``with client.session_begin()``. Exceptions propagate to the caller.
        """
        return self._session_factory.begin()

    def dispose(self) -> None:
        """Dispose the pool; close sessions and release connections first.

        Borrowed connections stay open. The engine can create a new pool later.
        """
        self._engine.dispose()
