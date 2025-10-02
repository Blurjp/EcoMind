from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db import Base


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Org(Base):
    __tablename__ = "orgs"

    id = Column(String, primary_key=True, default=lambda: f"org_{uuid.uuid4().hex[:12]}")
    name = Column(String, nullable=False)
    plan = Column(SQLEnum(PlanType), default=PlanType.FREE)
    created_at = Column(DateTime, default=datetime.utcnow)
