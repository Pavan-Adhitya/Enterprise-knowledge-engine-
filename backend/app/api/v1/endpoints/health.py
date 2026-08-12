import time
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()
START_TIME = time.time()


@router.get("/health", summary="Health Check")
async def health_check():
    """System health check endpoint returning service status, uptime, and settings."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "llm_model": settings.DEFAULT_LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL
    }
