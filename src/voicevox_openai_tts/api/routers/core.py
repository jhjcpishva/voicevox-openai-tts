from fastapi import APIRouter

router = APIRouter()


@router.get("/v1/models", summary="利用可能なAPIモデル一覧を取得")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "voicevox-v1",
                "object": "model",
                "created": 0,
                "owned_by": "voicevox-openai-tts",
            }
        ],
    }


@router.get("/health", summary="アプリケーションの疎通確認")
async def health():
    """
    アプリケーションの疎通確認用エンドポイント。
    """
    return {"status": "ok"}
