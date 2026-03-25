from fastapi import APIRouter, HTTPException, Response

from ..schemas.speech import SpeechRequest
from ...services.tts import TTSService, TTSServiceError, InvalidVoiceError

router = APIRouter()


@router.post("/v1/audio/speech", summary="テキストを音声に変換")
async def create_speech(request: SpeechRequest):
    """
    テキストを音声に変換するエンドポイント（OpenAI TTS API互換）

    Args:
        request: 音声合成リクエスト

    Returns:
        Response: 音声データを含むHTTPレスポンス

    Raises:
        HTTPException: VOICEVOXエンジンとの通信に失敗した場合
    """
    tts_service = TTSService()

    try:
        audio_data, media_type = await tts_service.synthesize_speech(
            text=request.input,
            voice=request.voice,
            speed=request.speed,
        )
        return Response(content=audio_data, media_type=media_type)
    except InvalidVoiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except TTSServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
