from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="アプリケーションの疎通確認")
async def health():
    """
    アプリケーションの疎通確認用エンドポイント。
    """
    return {"status": "ok"}
