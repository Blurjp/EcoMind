from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
import uuid

from app.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: f"audit_{uuid.uuid4().hex[:16]}")
    org_id = Column(String, nullable=False, index=True)
    user_id = Column(String)
    action = Column(String, nullable=False)  # e.g., "create_user", "update_factors"
    resource = Column(String, nullable=False)  # e.g., "users", "factors_overrides"
    details = Column(JSON)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
