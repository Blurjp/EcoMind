from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.post("/ingest")
async def ingest_placeholder():
    """
    Placeholder for ingest endpoint.
    Real ingestion happens via Gateway → Kafka → Worker.
    This exists for direct API access if needed.
    """
    return {
        "status": "use_gateway",
        "message": "Please use Gateway service at /v1/ingest for high-throughput ingestion",
        "ts": datetime.utcnow().isoformat() + "Z",
    }