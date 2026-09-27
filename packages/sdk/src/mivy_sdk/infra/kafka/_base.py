"""Internal lifecycle templates for synchronous and asynchronous Kafka clients."""

import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from types import TracebackType
from typing import Self

from confluent_kafka import Consumer, Producer
from confluent_kafka.aio import AIOConsumer, AIOProducer

from .config import KafkaConfig


def _raise_errors(message: str, errors: list[BaseException]) -> None:
    """Preserve all failures, including failures discovered while cleaning up."""
    unique: list[BaseException] = []
    seen: set[int] = set()
    for error in errors:
        if id(error) not in seen:
            unique.append(error)
            seen.add(id(error))
    if len(unique) == 1:
        raise unique[0]
    if unique:
        raise BaseExceptionGroup(message, unique)


class KafkaClientBase[ClientT: (Producer, Consumer)](ABC):
    def __init__(self, config: KafkaConfig) -> None:
        self._config = config
        self._client: ClientT | None = None
        self._closed = False

    @property
    def _connected_client(self) -> ClientT:
        if self._closed or self._client is None:
            raise RuntimeError(f"{type(self).__name__} is not connected")
        return self._client

    @abstractmethod
    def _create_client(self) -> ClientT:
        """Create the native client; metadata validation belongs to connect()."""

    @abstractmethod
    def _close_client(self, client: ClientT) -> None:
        """Finish client-specific work and release the native client."""

    def connect(self, timeout: float = 10) -> None:
        """Check metadata; topic permissions and group assignment remain separate."""
        if self._closed:
            raise RuntimeError(f"A closed {type(self).__name__} cannot be reconnected")
        if self._client is not None:
            return
        try:
            self._client = self._create_client()
            self._client.list_topics(timeout=timeout)
        except BaseException as error:
            errors = [error]
            try:
                self.close()
            except BaseException as cleanup_error:
                errors.append(cleanup_error)
            _raise_errors(
                f"{type(self).__name__} connection and cleanup failed", errors
            )

    def close(self) -> None:
        """Close once after callers stop using the native client."""
        if self._closed:
            return
        self._closed = True
        client, self._client = self._client, None
        if client is not None:
            self._close_client(client)

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncKafkaClientBase[ClientT: (AIOProducer, AIOConsumer)](ABC):
    _executor_workers = 2

    def __init__(self, config: KafkaConfig) -> None:
        self._config = config
        self._client: ClientT | None = None
        self._executor: ThreadPoolExecutor | None = None
        self._closed = False
        self._close_task: asyncio.Task[None] | None = None

    @property
    def _connected_client(self) -> ClientT:
        if self._closed or self._client is None:
            raise RuntimeError(f"{type(self).__name__} is not connected")
        return self._client

    @abstractmethod
    def _create_client(self, executor: ThreadPoolExecutor) -> ClientT:
        """Create the native client using the executor owned by this instance."""

    @abstractmethod
    async def _close_client(self, client: ClientT) -> None:
        """Finish client-specific work before the executor is released."""

    async def connect(self, timeout: float = 10) -> None:
        """Create in the current event loop and check metadata with native timeout."""
        if self._closed:
            raise RuntimeError(f"A closed {type(self).__name__} cannot be reconnected")
        if self._client is not None:
            return
        try:
            self._executor = ThreadPoolExecutor(max_workers=self._executor_workers)
            self._client = self._create_client(self._executor)
            await self._client.list_topics(timeout=timeout)
        except BaseException as error:
            errors = [error]
            try:
                await self.close()
            except BaseException as cleanup_error:
                errors.append(cleanup_error)
            _raise_errors(
                f"{type(self).__name__} connection and cleanup failed", errors
            )

    async def _close(self) -> None:
        errors: list[BaseException] = []
        client, self._client = self._client, None
        executor, self._executor = self._executor, None
        if client is not None:
            try:
                await self._close_client(client)
            except BaseException as error:
                errors.append(error)
        # Creation may fail after allocating the executor but before returning a client.
        if executor is not None:
            try:
                await asyncio.to_thread(executor.shutdown, wait=True)
            except BaseException as error:
                errors.append(error)
        _raise_errors(f"{type(self).__name__} cleanup failed", errors)

    async def close(self) -> None:
        """Share one cleanup task; cancelling its waiter does not cancel cleanup."""
        if self._close_task is None:
            self._closed = True
            self._close_task = asyncio.create_task(self._close())
            # Observe a failure even if every caller stops awaiting cleanup.
            self._close_task.add_done_callback(
                lambda task: task.exception() if not task.cancelled() else None
            )
        await asyncio.shield(self._close_task)

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()
