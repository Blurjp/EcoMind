from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models.alert import Alert, AlertChannel

router = APIRouter()


class AlertCreate(BaseModel):
    org_id: str
    name: str
    metric: str
    threshold: float
    window: str
    channel: AlertChannel
    webhook_url: str | None = None


class AlertResponse(BaseModel):
    id: str
    org_id: str
    name: str
    metric: str
    threshold: float
    window: str
    channel: AlertChannel
    webhook_url: str | None
    enabled: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    db_alert = Alert(
        org_id=alert.org_id,
        name=alert.name,
        metric=alert.metric,
        threshold=alert.threshold,
        window=alert.window,
        channel=alert.channel,
        webhook_url=alert.webhook_url,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/orgs/{org_id}/alerts", response_model=list[AlertResponse])
async def list_alerts(org_id: str, db: Session = Depends(get_db)):
    """List alerts for an organization"""
    alerts = db.query(Alert).filter(Alert.org_id == org_id).all()
    return alerts


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"status": "deleted", "id": alert_id}