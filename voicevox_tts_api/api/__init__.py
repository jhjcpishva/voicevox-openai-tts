from fastapi import FastAPI
from .routers import models, speech


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成し、ルーターを設定します。
    """
    app = FastAPI(
        title="VOICEVOX OpenAI TTS API",
        description="VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
        version="1.0.0",
    )

    # ルーターの登録
    app.include_router(models.router)
    app.include_router(speech.router)

    return app
