"""
API統合テスト
"""

import pytest
from httpx import ASGITransport, AsyncClient

from voicevox_openai_tts.api.create_app import create_app
from voicevox_openai_tts.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def app():
    """テスト用のFastAPIアプリケーションを提供するフィクスチャ"""
    return create_app()


@pytest.mark.asyncio
class TestCoreEndpoints:
    """コアエンドポイントの統合テスト"""

    async def test_health_endpoint(self, app):
        """ヘルスチェックエンドポイントが動作すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
class TestCorsConfiguration:
    """CORS設定の統合テスト"""

    async def test_cors_headers_are_not_added_when_allow_origins_is_unset(
        self, monkeypatch
    ):
        """ALLOW_ORIGINS 未指定時は CORS ヘッダーを返さないこと"""
        monkeypatch.delenv("ALLOW_ORIGINS", raising=False)
        app = create_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/health", headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers

    async def test_cors_headers_are_added_for_single_allowed_origin(self, monkeypatch):
        """単一オリジン指定時は一致した Origin を許可すること"""
        monkeypatch.setenv("ALLOW_ORIGINS", "https://example.com")
        app = create_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/health", headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "https://example.com"

    async def test_cors_headers_are_added_for_matching_origin_in_list(
        self, monkeypatch
    ):
        """複数オリジン指定時は一致した Origin のみ許可すること"""
        monkeypatch.setenv(
            "ALLOW_ORIGINS", "https://example.com, http://localhost:3000"
        )
        app = create_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/health", headers={"Origin": "http://localhost:3000"}
            )

        assert response.status_code == 200
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )

    async def test_cors_headers_support_wildcard_origin(self, monkeypatch):
        """ワイルドカード指定時は任意の Origin を許可すること"""
        monkeypatch.setenv("ALLOW_ORIGINS", "*")
        app = create_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/health", headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "*"


@pytest.mark.asyncio
class TestVoicesEndpoints:
    """音声エンドポイントの統合テスト"""

    async def test_voices_endpoint_exists(self, app):
        """/v1/audio/voices エンドポイントが存在すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/v1/audio/voices")

        # エラーがなく、適切なレスポンスが返されることを確認
        assert response.status_code in [
            200,
            500,
            504,
            502,
            503,
        ]  # 正常またはVOICEVOX接続エラー
        if response.status_code == 200:
            data = response.json()
            assert "voices" in data


@pytest.mark.asyncio
class TestSpeechEndpoints:
    """音声合成エンドポイントの統合テスト"""

    async def test_openapi_describes_engine_support(self, app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/openapi.json")
        schemas = response.json()["components"]["schemas"]
        options = schemas["VoicevoxOptions"]["properties"]
        assert "両方対応" in options["volume_scale"]["description"]
        assert "AivisSpeech専用" in options["tempo_dynamics_scale"]["description"]
        assert "VOICEVOX専用" in options["pause_length"]["description"]
        assert all("description" in field for field in options.values())
        assert (
            "判定せず"
            in schemas["SpeechRequest"]["properties"]["voicevox"]["description"]
        )

    async def test_speech_passes_voicevox_options(self, app, monkeypatch):
        async def synthesize(_self, **kwargs):
            assert kwargs["speed"] == 1.1
            assert kwargs["voicevox_options"] == {
                "intonationScale": 1.2,
                "tempoDynamicsScale": 0.8,
                "pitchScale": -0.1,
                "volumeScale": 0.0,
                "prePhonemeLength": 0.0,
                "postPhonemeLength": 0.2,
                "pauseLength": 0.3,
                "pauseLengthScale": 0.8,
                "enable_interrogative_upspeak": False,
            }
            return b"audio", "audio/wav"

        monkeypatch.setattr(
            "voicevox_openai_tts.services.speech.SpeechService.synthesize_speech",
            synthesize,
        )
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/audio/speech",
                json={
                    "model": "voicevox-v1",
                    "input": "テスト",
                    "voice": "1",
                    "speed": 1.1,
                    "voicevox": {
                        "intonation_scale": 1.2,
                        "tempo_dynamics_scale": 0.8,
                        "pitch_scale": -0.1,
                        "volume_scale": 0,
                        "pre_phoneme_length": 0,
                        "post_phoneme_length": 0.2,
                        "pause_length": 0.3,
                        "pause_length_scale": 0.8,
                        "enable_interrogative_upspeak": False,
                    },
                },
            )
        assert response.status_code == 200
        assert response.content == b"audio"

    @pytest.mark.parametrize(
        "options",
        [
            {"intonation_scale": -0.1},
            {"intonation_scale": 2.1},
            {"tempo_dynamics_scale": -0.1},
            {"tempo_dynamics_scale": 2.1},
            {"pitch_scale": -0.16},
            {"pitch_scale": 0.16},
            {"volume_scale": -0.1},
            {"volume_scale": 2.1},
            {"pre_phoneme_length": -0.1},
            {"post_phoneme_length": -0.1},
            {"pause_length": -0.1},
            {"pause_length_scale": -0.1},
            {"volume_scale": "NaN"},
            {"pre_phoneme_length": "Infinity"},
            {"speed_scale": 1.1},
            {"volume_sclae": 1},
        ],
    )
    async def test_speech_rejects_invalid_voicevox_options(self, app, options):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/audio/speech",
                json={
                    "model": "voicevox-v1",
                    "input": "テスト",
                    "voice": "1",
                    "voicevox": options,
                },
            )
        assert response.status_code == 422

    async def test_speech_endpoint_validation(self, app):
        """音声合成エンドポイントのバリデーションが動作すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/audio/speech",
                json={
                    "model": "voicevox-v1",
                    "input": "テスト",
                    "voice": "invalid_voice",
                },
            )

        # 無効な音声指定で400エラーが返されることを確認
        assert response.status_code == 400

    async def test_speech_endpoint_rejects_unsupported_response_format(self, app):
        """未対応のレスポンス形式を拒否すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/audio/speech",
                json={
                    "model": "voicevox-v1",
                    "input": "テスト",
                    "voice": "alloy",
                    "response_format": "opus",
                },
            )

        assert response.status_code == 422
