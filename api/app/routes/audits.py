from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db import get_db
from app.models.audit import AuditLog

router = APIRouter()


@router.get("/audits")
async def list_audits(
    org_id: str = Query(...),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """List audit logs for an organization"""
    logs = db.query(AuditLog).filter(
        AuditLog.org_id == org_id
    ).order_by(desc(AuditLog.ts)).limit(limit).all()

    return {
        "org_id": org_id,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "details": log.details,
                "ts": log.ts.isoformat() + "Z" if log.ts else None,
            }
            for log in logs
        ],
    }
