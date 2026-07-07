from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/info",
    tags=["Info"],
)


@router.get("/")
async def info():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
    }