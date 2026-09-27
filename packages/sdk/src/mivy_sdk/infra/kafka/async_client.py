"""Asyncio clients; native callbacks and partition handling stay accessible."""

import asyncio
import math
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from confluent_kafka import KafkaException, Message, TopicPartition
from confluent_kafka.aio import AIOConsumer, AIOProducer

from ._base import AsyncKafkaClientBase, _raise_errors
from .config import KafkaConfig


class AsyncKafkaProducer(AsyncKafkaClientBase[AIOProducer]):
    _executor_workers = 4

    def __init__(
        self, config: KafkaConfig, *, batch_size: int = 1, buffer_timeout: float = 0.1
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        if not math.isfinite(buffer_timeout) or buffer_timeout < 0:
            raise ValueError("buffer_timeout must be finite and nonnegative")
        super().__init__(config)
        self._batch_size = batch_size
        self._buffer_timeout = buffer_timeout
        self._pending: set[asyncio.Task[Message]] = set()
        self._detached: set[asyncio.Task[Message]] = set()
        self._delivery_errors: list[BaseException] = []
        self._delivery_report_only_error = False

    @property
    def producer(self) -> AIOProducer:
        return self._connected_client

    def _create_client(self, executor: ThreadPoolExecutor) -> AIOProducer:
        options = self._config.producer_config()
        producer = AIOProducer(
            options,
            executor=executor,
            batch_size=self._batch_size,
            buffer_timeout=self._buffer_timeout,
        )
        self._delivery_report_only_error = (
            options.get("delivery.report.only.error") is True
        )
        return producer

    async def _send(
        self, producer: AIOProducer, topic: str, value: bytes | None, key: bytes | None
    ) -> Message:
        delivery = await producer.produce(topic, value=value, key=key)
        return cast(Message, await delivery)

    def _observe_send(self, task: asyncio.Task[Message]) -> None:
        self._pending.discard(task)
        error = task.exception() if not task.cancelled() else None
        if task in self._detached:
            self._detached.discard(task)
            if error is not None:
                self._delivery_errors.append(error)

    async def publish_and_wait(
        self, topic: str, value: bytes | None, *, key: bytes | None = None
    ) -> Message:
        """Wait for delivery; cancellation does not withdraw the Kafka send.

        Detached delivery failures are surfaced by close(). Native async headers
        are unsupported; serialization belongs to the caller.
        """
        producer = self.producer
        # Without successful delivery callbacks the delivery Future stays pending.
        if self._delivery_report_only_error:
            raise ValueError(
                "publish_and_wait requires delivery.report.only.error=False"
            )
        if self._buffer_timeout == 0:
            raise ValueError("publish_and_wait requires buffer_timeout > 0")
        task = asyncio.create_task(self._send(producer, topic, value, key))
        self._pending.add(task)
        task.add_done_callback(self._observe_send)
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            self._detached.add(task)
            if task.done():
                self._observe_send(task)
            raise

    async def _close_client(self, producer: AIOProducer) -> None:
        errors: list[BaseException] = []
        if self._pending:
            results = await asyncio.gather(*self._pending, return_exceptions=True)
            errors.extend(
                result for result in results if isinstance(result, BaseException)
            )
        errors.extend(self._delivery_errors)
        self._delivery_errors.clear()
        try:
            await producer.close()
        except BaseException as error:
            errors.append(error)
        _raise_errors("Kafka producer delivery or cleanup failed", errors)


class AsyncKafkaConsumer(AsyncKafkaClientBase[AIOConsumer]):
    @property
    def consumer(self) -> AIOConsumer:
        return self._connected_client

    def _create_client(self, executor: ThreadPoolExecutor) -> AIOConsumer:
        return AIOConsumer(self._config.consumer_config(), executor=executor)

    async def commit_offsets(
        self, offsets: list[TopicPartition]
    ) -> list[TopicPartition]:
        """Wait for explicit next-offset commits, including per-partition checks."""
        result = cast(
            list[TopicPartition],
            await self.consumer.commit(offsets=offsets, asynchronous=False),
        )
        # Native commit can return partition failures without raising an exception.
        errors: list[BaseException] = [
            KafkaException(item.error) for item in result if item.error is not None
        ]
        _raise_errors("Kafka offset commits failed", errors)
        return result

    async def _close_client(self, consumer: AIOConsumer) -> None:
        """Call after polling stops; native auto-commit settings apply on close."""
        await consumer.close()
