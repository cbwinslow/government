"""Typed OpenDiscourse configuration with environment-variable overrides."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dsn: SecretStr = SecretStr(
        "postgresql+psycopg://opendiscourse:opendiscourse@localhost:5432/opendiscourse"
    )
    pool_size: int = Field(default=10, ge=1, le=100)
    statement_timeout_seconds: int = Field(default=300, ge=1)


class StorageSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root: Path = Path("./data")
    temp_root: Path = Path("./data/.tmp")
    checksum_algorithm: Literal["sha256"] = "sha256"


class HttpSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timeout_seconds: int = Field(default=60, ge=1, le=3600)
    max_retries: int = Field(default=5, ge=0, le=20)
    user_agent: str = "OpenDiscourse/0.1 (+https://github.com/cbwinslow/government)"

    @field_validator("user_agent")
    @classmethod
    def user_agent_must_be_identifiable(cls, value: str) -> str:
        if not value.strip() or value.lower() in {"python", "requests", "httpx"}:
            raise ValueError("user_agent must identify OpenDiscourse")
        return value


class IngestionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    download_concurrency: int = Field(default=8, ge=1, le=128)
    extract_concurrency: int = Field(default=4, ge=1, le=128)
    fail_fast: bool = False


class SourceSecrets(BaseModel):
    model_config = ConfigDict(extra="forbid")

    govinfo_api_key: SecretStr | None = None
    congress_api_key: SecretStr | None = None
    fec_api_key: SecretStr | None = None
    census_api_key: SecretStr | None = None
    fred_api_key: SecretStr | None = None
    openstates_api_key: SecretStr | None = None


class Settings(BaseSettings):
    """Application settings.

    Environment variables override values loaded from TOML. Nested values use
    double underscores, for example ``OPENDISCOURSE_STORAGE__ROOT``.
    """

    model_config = SettingsConfigDict(
        env_prefix="OPENDISCOURSE_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=False,
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    config_file: Path = Path("config/default.toml")
    database: DatabaseSettings = DatabaseSettings()
    storage: StorageSettings = StorageSettings()
    http: HttpSettings = HttpSettings()
    ingestion: IngestionSettings = IngestionSettings()
    sources: SourceSecrets = SourceSecrets()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        del settings_cls
        return env_settings, dotenv_settings, init_settings, file_secret_settings

    def redacted_dict(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data["database"]["dsn"] = "**********"
        data["sources"] = {
            key: ("**********" if value else None) for key, value in data["sources"].items()
        }
        return data


def load_settings(config_path: Path | str | None = None) -> Settings:
    """Load TOML defaults and allow environment variables to override them."""

    path = Path(config_path) if config_path is not None else Path("config/default.toml")
    values: dict[str, Any] = {}
    if config_path is not None and not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    if path.exists():
        with path.open("rb") as handle:
            values = tomllib.load(handle)
    values["config_file"] = path
    return Settings(**values)
