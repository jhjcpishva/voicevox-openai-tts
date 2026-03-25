from fastapi import APIRouter, HTTPException

from ..schemas.voices import AudioVoicesResponse
from ...services.voice import VoiceService

router = APIRouter()


@router.get("/v1/audio/voices", summary="利用可能な音声一覧を取得")
async def list_audio_voices() -> AudioVoicesResponse:
    """
    OpenWebUI 互換の音声一覧を返します。

    Returns:
        AudioVoicesResponse: 利用可能な音声情報のリスト

    Raises:
        HTTPException: VOICEVOXエンジンとの通信に失敗した場合
    """
    voice_service = VoiceService()

    try:
        voices = await voice_service.get_available_voices()
        return AudioVoicesResponse(voices=voices)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}"
        )
