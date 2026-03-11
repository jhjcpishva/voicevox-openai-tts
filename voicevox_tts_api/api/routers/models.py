from fastapi import APIRouter

router = APIRouter()


@router.get("/v1/models", summary="利用可能なモデル一覧を取得")
async def list_models():
    """
    利用可能なモデルの一覧を返します。
    現在はVOICEVOXモデルのみをサポートしています。
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "voicevox-v1",
                "object": "model",
                "owned_by": "VOICEVOX",
                "permission": [],
            }
        ],
    }
