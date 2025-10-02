from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ts": datetime.utcnow().isoformat() + "Z",
    }