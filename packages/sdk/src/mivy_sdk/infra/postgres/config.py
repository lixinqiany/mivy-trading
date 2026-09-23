"""PostgreSQL connection configuration."""

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from sqlalchemy.engine import URL


class PostgresConfig(BaseModel):
    """Validate supplied values without reading environment variables or files."""

    model_config = ConfigDict(
        extra="forbid",  # throw an error if any extra fields are provided
        frozen=True,  # make the attribute value immutable after creation
        hide_input_in_errors=False,  # if True， errors don't include the input value
    )

    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    db: str = Field(min_length=1)
    user: str = Field(min_length=1)
    password: SecretStr = Field(min_length=1)

    @property
    def url(self) -> URL:
        """Build a psycopg URL usable by both sync and async engines."""
        return URL.create(
            "postgresql+psycopg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        )
