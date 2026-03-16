FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt ./pyproject.toml ./README.md ./
COPY ./src ./src
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "voicevox_openai_tts.main:app", "--host", "0.0.0.0", "--port", "8000"]
