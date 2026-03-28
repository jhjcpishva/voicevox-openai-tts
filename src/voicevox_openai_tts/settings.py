from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
