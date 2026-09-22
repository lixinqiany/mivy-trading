"""Pool configuration for sync and async engines."""

import dataclasses
from math import isfinite
from typing import TypedDict, cast

from sqlalchemy.pool import NullPool, Pool

from mivy_contracts.protocols.common import SupportsAsDict


class EnginePoolOptions(TypedDict, total=False):
    """Pool keyword arguments accepted by SQLAlchemy engine factories."""

    poolclass: type[Pool]
    pool_size: int
    max_overflow: int
    pool_timeout: float
    pool_pre_ping: bool


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PostgresPoolOptions(SupportsAsDict[EnginePoolOptions]):
    """Pool settings, validated even when pooling is disabled.

    pool_timeout limits the wait for a free connection, not SQL execution time.
    """

    enabled: bool = True
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_pre_ping: bool = True

    def __post_init__(self) -> None:
        if self.pool_size <= 0:
            raise ValueError("Pool size must be positive")
        if self.max_overflow < 0:
            raise ValueError("Pool max_overflow must be non-negative")
        if not isfinite(self.pool_timeout) or self.pool_timeout <= 0:
            raise ValueError("Pool timeout must be positive and finite")

    def asdict(self) -> EnginePoolOptions:
        """Export engine kwargs: omit enabled, or return only poolclass=NullPool."""
        if not self.enabled:
            return {"poolclass": NullPool}
        options = dataclasses.asdict(self)
        options.pop("enabled")
        # asdict erases field types; remaining fields match EnginePoolOptions.
        return cast(EnginePoolOptions, options)
