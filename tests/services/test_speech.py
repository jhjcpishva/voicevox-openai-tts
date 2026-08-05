import logging

import httpx
import pytest

from voicevox_openai_tts.services.speech import (
    SpeechService,
    InvalidVoiceError,
    SpeechServiceError,
)


class TestSpeechService:
    """SpeechServiceのユニットテスト"""

    def test_init_with_default_url(self):
        """デフォルトURLで初期化できること"""
        service = SpeechService()
        assert service.voicevox_url == "http://voicevox_engine:50021"
        assert service.timeout_seconds == 60.0

    def test_init_with_custom_url(self):
        """カスタムURLで初期化できること"""
        service = SpeechService("http://custom:50021", timeout_seconds=120.0)
        assert service.voicevox_url == "http://custom:50021"
        assert service.timeout_seconds == 120.0

    def test_get_speaker_id_from_alias(self, monkeypatch):
        """エイリアスから正しいスピーカーIDを取得できること"""
        service = SpeechService()

        # voice_mappings をモック
        mock_mappings = {"alloy": "1", "echo": "2", "shimmer": "3"}
        monkeypatch.setattr(
            "voicevox_openai_tts.services.speech.load_voice_mappings",
            lambda: mock_mappings,
        )

        assert service._get_speaker_id("alloy") == 1
        assert service._get_speaker_id("echo") == 2
        assert service._get_speaker_id("shimmer") == 3

    def test_get_speaker_id_from_number(self, monkeypatch):
        """数値文字列から直接スピーカーIDを取得できること"""
        service = SpeechService()

        monkeypatch.setattr(
            "voicevox_openai_tts.services.speech.load_voice_mappings",
            lambda: {},
        )

        assert service._get_speaker_id("10") == 10
        assert service._get_speaker_id("50") == 50

    def test_get_speaker_id_raises_invalid_voice(self, monkeypatch):
        """無効な音声指定時にInvalidVoiceErrorが発生すること"""
        service = SpeechService()

        mock_mappings = {"alloy": "1", "echo": "2"}
        monkeypatch.setattr(
            "voicevox_openai_tts.services.speech.load_voice_mappings",
            lambda: mock_mappings,
        )

        with pytest.raises(InvalidVoiceError) as exc_info:
            service._get_speaker_id("invalid_voice")

        assert "Invalid voice: invalid_voice" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    def test_invalid_voice_error_message(self):
        """InvalidVoiceErrorのメッセージが正しく生成されること"""
        error = InvalidVoiceError("unknown", ["alloy", "echo", "shimmer"])

        assert "Invalid voice: unknown" in error.message
        assert "alloy" in error.message
        assert "echo" in error.message
        assert "shimmer" in error.message
        assert error.status_code == 400

    def test_speech_service_error(self):
        """SpeechServiceErrorが正しく初期化されること"""
        error = SpeechServiceError("Test error", status_code=500)

        assert error.message == "Test error"
        assert error.status_code == 500

    def test_speech_service_error_default_status_code(self):
        """SpeechServiceErrorがデフォルトのステータスコード500を持つこと"""
        error = SpeechServiceError("Test error")

        assert error.status_code == 500

    @pytest.mark.asyncio
    async def test_synthesize_speech_timeout_logs_and_returns_504(
        self, monkeypatch, caplog
    ):
        """エンジン通信タイムアウト時にログを出して504扱いにすること"""

        class TimeoutAsyncClient:
            timeout = None

            def __init__(self, timeout):
                TimeoutAsyncClient.timeout = timeout

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_value, traceback):
                return False

            async def post(self, url, params=None, json=None):
                raise httpx.TimeoutException("timed out")

        monkeypatch.setattr(
            "voicevox_openai_tts.services.speech.httpx.AsyncClient",
            TimeoutAsyncClient,
        )
        service = SpeechService("http://custom:50021", timeout_seconds=120.0)
        caplog.set_level(logging.WARNING, logger="voicevox_openai_tts.services.speech")

        with pytest.raises(SpeechServiceError) as exc_info:
            await service.synthesize_speech("テスト", "1")

        assert exc_info.value.status_code == 504
        assert TimeoutAsyncClient.timeout == 120.0
        assert "VOICEVOX engine request timed out" in caplog.text
        assert "engine_url=http://custom:50021" in caplog.text
        assert "timeout_seconds=120.0" in caplog.text
