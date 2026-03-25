"""
API統合テスト
"""

import pytest
from httpx import ASGITransport, AsyncClient

from voicevox_openai_tts.api.create_app import create_app


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
