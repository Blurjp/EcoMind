from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
import uuid
import enum

from app.db import Base


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    CSV = "csv"


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: f"report_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, nullable=False, index=True)
    report_type = Column(String, nullable=False)  # e.g., "esg", "usage"
    format = Column(SQLEnum(ReportFormat), nullable=False)
    from_date = Column(String)
    to_date = Column(String)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    download_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)