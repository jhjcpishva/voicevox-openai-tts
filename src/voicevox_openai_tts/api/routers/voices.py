import os

import httpx
from fastapi import APIRouter, HTTPException

from ..schemas.voices import AudioVoice
from ..schemas.voices import AudioVoicesResponse
from ..voice_mappings import load_voice_mappings

router = APIRouter()

DEFAULT_VOICEVOX_ENGINE_URL = "http://voicevox_engine:50021"


def build_voice_name(speaker_name: str, style_name: str) -> str:
    return f"{speaker_name} / {style_name}"


def flatten_speakers_to_voices(speakers: list[dict]) -> list[AudioVoice]:
    voices: list[AudioVoice] = []

    for speaker in speakers:
        speaker_name = speaker.get("name", "")

        for style in speaker.get("styles", []):
            style_id = style.get("id")
            style_name = style.get("name", "")

            if style_id is None:
                continue

            voices.append(
                AudioVoice(
                    id=str(style_id),
                    name=build_voice_name(speaker_name, style_name),
                )
            )

    return voices


def mapping_aliases_to_voices() -> list[AudioVoice]:
    return [AudioVoice(id=alias, name=alias) for alias in load_voice_mappings()]


@router.get("/v1/audio/voices", summary="利用可能な音声一覧を取得")
async def list_audio_voices() -> AudioVoicesResponse:
    """
    OpenWebUI 互換の音声一覧を返します。
    """
    voicevox_url = os.getenv("VOICEVOX_ENGINE_URL", DEFAULT_VOICEVOX_ENGINE_URL)
    speakers_url = f"{voicevox_url}/speakers"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(speakers_url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, detail=f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}"
        )

    style_voices = flatten_speakers_to_voices(response.json())
    alias_voices = mapping_aliases_to_voices()
    return AudioVoicesResponse(voices=style_voices + alias_voices)
