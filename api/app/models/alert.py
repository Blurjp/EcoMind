from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, Boolean
import uuid
import enum

from app.db import Base


class AlertChannel(str, enum.Enum):
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    EMAIL = "email"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: f"alert_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    metric = Column(String, nullable=False)  # e.g., "co2_kg", "kwh", "call_count"
    threshold = Column(Float, nullable=False)
    window = Column(String, nullable=False)  # e.g., "1h", "1d", "7d"
    channel = Column(SQLEnum(AlertChannel), nullable=False)
    webhook_url = Column(String)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: f"notif_{uuid.uuid4().hex[:16]}")
    alert_id = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    status = Column(String, default="sent")  # sent, failed
    ts = Column(DateTime, default=datetime.utcnow, index=True)