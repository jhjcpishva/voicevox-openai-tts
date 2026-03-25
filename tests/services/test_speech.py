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

    def test_init_with_custom_url(self):
        """カスタムURLで初期化できること"""
        service = SpeechService("http://custom:50021")
        assert service.voicevox_url == "http://custom:50021"

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
