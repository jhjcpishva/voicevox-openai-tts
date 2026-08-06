import logging

import httpx
import pytest

from voicevox_openai_tts.services.voice import VoiceService, SpeakerInfo
from voicevox_openai_tts.api.schemas.voices import AudioVoice


class TestVoiceService:
    """VoiceServiceのユニットテスト"""

    def test_init_with_default_url(self):
        """デフォルトURLで初期化できること"""
        service = VoiceService()
        assert service.voicevox_url == "http://voicevox_engine:50021"
        assert service.timeout_seconds == 60.0

    def test_init_with_custom_url(self):
        """カスタムURLで初期化できること"""
        service = VoiceService("http://custom:50021", timeout_seconds=120.0)
        assert service.voicevox_url == "http://custom:50021"
        assert service.timeout_seconds == 120.0

    def test_build_voice_name(self):
        """音声名の構築が正しく行われること"""
        service = VoiceService()
        result = service._build_voice_name("四国めたん", "あまあま")
        assert result == "四国めたん / あまあま"

    def test_flatten_speakers_to_voices(self):
        """話者情報のフラット化が正しく行われること"""
        service = VoiceService()
        speakers = [
            {
                "name": "四国めたん",
                "styles": [
                    {"id": 1, "name": "あまあま"},
                    {"id": 2, "name": "ツンツン"},
                ],
            },
            {
                "name": "ずんだもん",
                "styles": [
                    {"id": 3, "name": "あまあま"},
                ],
            },
        ]

        voices = service._flatten_speakers_to_voices(speakers)

        assert len(voices) == 3
        assert voices[0].id == "1"
        assert voices[0].name == "四国めたん / あまあま"
        assert voices[1].id == "2"
        assert voices[1].name == "四国めたん / ツンツン"
        assert voices[2].id == "3"
        assert voices[2].name == "ずんだもん / あまあま"

    def test_flatten_speakers_skips_missing_style_id(self):
        """style_idが欠けている場合はスキップされること"""
        service = VoiceService()
        speakers = [
            {
                "name": "テスト",
                "styles": [
                    {"id": 1, "name": "スタイル1"},
                    {"name": "スタイル2"},  # idなし
                ],
            },
        ]

        voices = service._flatten_speakers_to_voices(speakers)

        assert len(voices) == 1
        assert voices[0].id == "1"

    @pytest.mark.asyncio
    async def test_get_available_voices_timeout_logs(self, monkeypatch, caplog):
        """話者一覧取得タイムアウト時にログを出すこと"""

        class TimeoutAsyncClient:
            timeout = None

            def __init__(self, timeout):
                TimeoutAsyncClient.timeout = timeout

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_value, traceback):
                return False

            async def get(self, url):
                raise httpx.TimeoutException("timed out")

        monkeypatch.setattr(
            "voicevox_openai_tts.services.voice.httpx.AsyncClient",
            TimeoutAsyncClient,
        )
        service = VoiceService("http://custom:50021", timeout_seconds=120.0)
        caplog.set_level(logging.WARNING, logger="voicevox_openai_tts.services.voice")

        with pytest.raises(httpx.TimeoutException):
            await service.get_available_voices()

        assert TimeoutAsyncClient.timeout == 120.0
        assert "VOICEVOX engine speakers request timed out" in caplog.text
        assert "engine_url=http://custom:50021" in caplog.text
        assert "timeout_seconds=120.0" in caplog.text
