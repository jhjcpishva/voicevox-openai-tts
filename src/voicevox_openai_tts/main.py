"""Main module for voicevox-openai-tts."""

from voicevox_openai_tts.api.create_app import create_app
from voicevox_openai_tts.settings import get_settings

app = create_app()


def main():
    """Run the application with uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "voicevox_openai_tts.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
