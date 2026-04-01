from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from voicevox_openai_tts.settings import get_settings

from .routers import core, speech, voices


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成し、ルーターを設定します。
    """
    settings = get_settings()

    app = FastAPI(
        title="VOICEVOX OpenAI TTS API",
        description="VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
        version="0.3.1",
    )

    if settings.allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allow_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(core.router)
    app.include_router(voices.router)
    app.include_router(speech.router)

    return app
