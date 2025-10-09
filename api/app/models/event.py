from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class EventEnriched(Base):
    __tablename__ = "events_enriched"

    id = Column(String, primary_key=True, default=lambda: f"evt_{uuid.uuid4().hex[:16]}")
    org_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False)
    model = Column(String)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    node_type = Column(String)
    region = Column(String)
    kwh = Column(Float, nullable=False)
    water_l = Column(Float, nullable=False)
    co2_kg = Column(Float, nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    source = Column(String)
    event_metadata = Column('metadata', JSON)  # Renamed to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_events_org_ts', 'org_id', 'ts'),
        Index('ix_events_user_ts', 'user_id', 'ts'),
    )
