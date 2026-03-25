"""Main module for voicevox-openai-tts."""

from voicevox_openai_tts.api.create_app import create_app

app = create_app()


def main():
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run("voicevox_openai_tts.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
