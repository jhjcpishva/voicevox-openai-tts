from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

DEFAULT_APP_HOST = "0.0.0.0"
DEFAULT_APP_PORT = 8000
DEFAULT_VOICEVOX_ENGINE_URL = "http://voicevox_engine:50021"
DEFAULT_VOICE_MAPPINGS_PATH = "/app/voice_mappings.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_host: str = DEFAULT_APP_HOST
    app_port: int = DEFAULT_APP_PORT
    voicevox_engine_url: str = DEFAULT_VOICEVOX_ENGINE_URL
    voice_mappings_path: str = DEFAULT_VOICE_MAPPINGS_PATH
    allow_origins: list[str] | None = None

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_allow_origins(cls, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
            return origins or None

        if isinstance(value, list | tuple):
            origins = [origin.strip() for origin in value if origin.strip()]
            return origins or None

        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
