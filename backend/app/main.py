import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Ensure UTF-8 output encoding for Windows command line environments
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from app.core.config import settings
from app.core.security import setup_cors
from app.core.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Ensure storage directories exist
    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize SQLite database schema
    await init_db()
    print(f"[INFO] {settings.PROJECT_NAME} Backend initialized successfully.")
    print(f"[INFO] Storage directory: {settings.uploads_path}")
    print(f"[INFO] Vector DB directory: {settings.chroma_path}")
    
    yield
    
    print("[INFO] Shutting down backend service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Knowledge Engine API powered by RAG, ChromaDB, and Google Gemini.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root status endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "api_v1": f"{settings.API_V1_STR}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
