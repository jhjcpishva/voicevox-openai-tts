from voicevox_openai_tts.settings import DEFAULT_APP_HOST
from voicevox_openai_tts.settings import DEFAULT_APP_PORT
from voicevox_openai_tts.settings import DEFAULT_VOICEVOX_ENGINE_URL
from voicevox_openai_tts.settings import DEFAULT_VOICE_MAPPINGS_PATH
from voicevox_openai_tts.settings import Settings
from voicevox_openai_tts.settings import get_settings


class TestSettings:
    def teardown_method(self):
        get_settings.cache_clear()

    def test_settings_defaults(self):
        settings = Settings()

        assert settings.app_host == DEFAULT_APP_HOST
        assert settings.app_port == DEFAULT_APP_PORT
        assert settings.voicevox_engine_url == DEFAULT_VOICEVOX_ENGINE_URL
        assert settings.voice_mappings_path == DEFAULT_VOICE_MAPPINGS_PATH

    def test_settings_read_environment_variables(self, monkeypatch):
        monkeypatch.setenv("APP_HOST", "127.0.0.1")
        monkeypatch.setenv("APP_PORT", "9000")
        monkeypatch.setenv("VOICEVOX_ENGINE_URL", "http://localhost:50021")
        monkeypatch.setenv("VOICE_MAPPINGS_PATH", "/tmp/voice_mappings.json")

        settings = Settings()

        assert settings.app_host == "127.0.0.1"
        assert settings.app_port == 9000
        assert settings.voicevox_engine_url == "http://localhost:50021"
        assert settings.voice_mappings_path == "/tmp/voice_mappings.json"

    def test_get_settings_is_cached(self):
        first = get_settings()
        second = get_settings()

        assert first is second
