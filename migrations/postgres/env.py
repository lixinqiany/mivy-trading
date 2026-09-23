from logging.config import fileConfig

from alembic import context
from pydantic_settings import BaseSettings, SettingsConfigDict

from mivy_contracts.db import Base
from mivy_sdk.infra.postgres import (
    PostgresClient,
    PostgresConfig,
    PostgresPoolOptions,
)


class MigrationSettings(BaseSettings):
    """Load PostgreSQL settings from the environment or working-directory .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
    )

    postgres: PostgresConfig


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    settings = MigrationSettings()
    context.configure(
        url=settings.postgres.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    settings = MigrationSettings()
    client = PostgresClient(
        settings.postgres,
        pool_options=PostgresPoolOptions(enabled=False),
    )
    try:
        with client.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    finally:
        client.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
