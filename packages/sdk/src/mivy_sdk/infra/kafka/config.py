"""Kafka connection settings supplied by the application."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

type SaslMechanism = Literal[
    "PLAIN",
    "SCRAM-SHA-256",
    "SCRAM-SHA-512",
    "GSSAPI",
    "OAUTHBEARER",
]

_CONNECTION_KEYS = {
    "bootstrap.servers",
    "metadata.broker.list",
    "security.protocol",
    "client.id",
    "sasl.mechanism",
    "sasl.mechanisms",
    "sasl.username",
    "sasl.password",
}


def _check_connection_keys(options: dict[str, object]) -> None:
    duplicates = _CONNECTION_KEYS.intersection(options)
    if duplicates:
        names = ", ".join(sorted(duplicates))
        raise ValueError(f"Use KafkaConfig connection fields for: {names}")


class KafkaConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    bootstrap_servers: str = Field(min_length=1)
    security_protocol: Literal["PLAINTEXT", "SASL_PLAINTEXT", "SSL", "SASL_SSL"] = (
        "PLAINTEXT"
    )
    sasl_mechanism: SaslMechanism | None = None
    username: str | None = Field(default=None, min_length=1)
    password: SecretStr | None = None
    client_id: str | None = Field(default=None, min_length=1)
    producer_options: dict[str, object] = Field(default_factory=dict)
    consumer_options: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _reject_duplicate_connection_options(self) -> Self:
        for options in (self.producer_options, self.consumer_options):
            _check_connection_keys(options)
        return self

    def _connection_options(self) -> dict[str, object]:
        # Recheck mutable option dictionaries, including values supplied by model_copy.
        _check_connection_keys(self.producer_options)
        _check_connection_keys(self.consumer_options)
        result: dict[str, object] = {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
        }
        for key, value in (
            ("sasl.mechanism", self.sasl_mechanism),
            ("sasl.username", self.username),
            ("client.id", self.client_id),
        ):
            if value is not None:
                result[key] = value
        if self.password is not None:
            result["sasl.password"] = self.password.get_secret_value()
        return result

    def producer_config(self) -> dict[str, object]:
        return {
            "acks": "all",
            "enable.idempotence": True,
            **self._connection_options(),
            **self.producer_options,
        }

    def consumer_config(self) -> dict[str, object]:
        return {
            "enable.auto.commit": False,
            "enable.auto.offset.store": False,
            "auto.offset.reset": "earliest",
            **self._connection_options(),
            **self.consumer_options,
        }
