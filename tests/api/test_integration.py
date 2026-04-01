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
            502,
            503,
        ]  # 正常またはVOICEVOX接続エラー
        if response.status_code == 200:
            data = response.json()
            assert "voices" in data


@pytest.mark.asyncio
class TestSpeechEndpoints:
    """音声合成エンドポイントの統合テスト"""

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
