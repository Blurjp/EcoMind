from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
import uuid
import enum

from app.db import Base


class Role(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    BILLING = "billing"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: f"user_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    role = Column(SQLEnum(Role), default=Role.VIEWER)
    created_at = Column(DateTime, default=datetime.utcnow)
