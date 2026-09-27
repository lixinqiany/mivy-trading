"""Synchronous Kafka clients with explicit ownership of their native clients."""

from concurrent.futures import Future

from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    Message,
    Producer,
    TopicPartition,
)

from ._base import KafkaClientBase, _raise_errors
from .config import KafkaConfig


class KafkaProducer(KafkaClientBase[Producer]):
    def __init__(self, config: KafkaConfig) -> None:
        super().__init__(config)
        self._delivery_report_only_error = False
        self._pending: set[Future[Message]] = set()

    @property
    def producer(self) -> Producer:
        """Native producer; callers service callbacks for their own produce calls."""
        return self._connected_client

    def _create_client(self) -> Producer:
        options = self._config.producer_config()
        producer = Producer(options)
        self._delivery_report_only_error = (
            options.get("delivery.report.only.error") is True
        )
        return producer

    def publish_and_wait(
        self, topic: str, value: bytes | None, *, key: bytes | None = None
    ) -> Message:
        """Wait for this message's delivery result under the configured acks policy."""
        producer = self.producer
        # Without successful delivery callbacks this wait could never finish.
        if self._delivery_report_only_error:
            raise ValueError(
                "publish_and_wait requires delivery.report.only.error=False"
            )
        result: Future[Message] = Future()

        def delivered(error: KafkaError | None, message: Message) -> None:
            if error is not None:
                result.set_exception(KafkaException(error))
            else:
                result.set_result(message)

        producer.produce(topic, value=value, key=key, on_delivery=delivered)
        self._pending.add(result)
        while not result.done():
            producer.poll(0.1)
        try:
            return result.result()
        finally:
            # A poll interruption leaves the result owned by close(), rather than
            # silently losing a delivery failure that arrives while draining.
            self._pending.discard(result)

    def _close_client(self, producer: Producer) -> None:
        """Drain queued sends and close; native delivery timeouts still apply."""
        errors: list[BaseException] = []
        try:
            remaining = producer.flush()
            if remaining:
                raise RuntimeError(
                    f"Kafka producer still has {remaining} queued messages"
                )
        except BaseException as error:
            errors.append(error)
        try:
            # The 2.15.1 wheel implements close(), but omits it from its stub.
            producer.close()  # type: ignore[attr-defined]
        except BaseException as error:
            errors.append(error)
        for result in tuple(self._pending):
            if result.done():
                delivery_error = result.exception()
                if delivery_error is not None:
                    errors.append(delivery_error)
                self._pending.discard(result)
        _raise_errors("Kafka producer cleanup failed", errors)


class KafkaConsumer(KafkaClientBase[Consumer]):
    @property
    def consumer(self) -> Consumer:
        """Native consumer; one reading loop owns polling and rebalance handling."""
        return self._connected_client

    def _create_client(self) -> Consumer:
        return Consumer(self._config.consumer_config())

    def commit_offsets(self, offsets: list[TopicPartition]) -> list[TopicPartition]:
        """Commit explicit next offsets; the caller determines safe progress."""
        result = self.consumer.commit(offsets=offsets, asynchronous=False)
        # Native commit can return partition failures without raising an exception.
        errors: list[BaseException] = [
            KafkaException(item.error) for item in result if item.error is not None
        ]
        _raise_errors("Kafka offset commits failed", errors)
        return result

    def _close_client(self, consumer: Consumer) -> None:
        """Close after polling stops; native auto-commit settings apply on close."""
        consumer.close()
