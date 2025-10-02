from datetime import date
from sqlalchemy import Column, String, Integer, Float, Date, Index

from app.db import Base


class DailyOrgAgg(Base):
    __tablename__ = "daily_org_agg"

    date = Column(Date, primary_key=True)
    org_id = Column(String, primary_key=True)
    call_count = Column(Integer, default=0)
    kwh = Column(Float, default=0.0)
    water_l = Column(Float, default=0.0)
    co2_kg = Column(Float, default=0.0)

    __table_args__ = (
        Index('ix_daily_org_date', 'date', 'org_id'),
    )


class DailyUserAgg(Base):
    __tablename__ = "daily_user_agg"

    date = Column(Date, primary_key=True)
    org_id = Column(String, primary_key=True)
    user_id = Column(String, primary_key=True)
    call_count = Column(Integer, default=0)
    kwh = Column(Float, default=0.0)
    water_l = Column(Float, default=0.0)
    co2_kg = Column(Float, default=0.0)


class DailyProviderAgg(Base):
    __tablename__ = "daily_provider_agg"

    date = Column(Date, primary_key=True)
    org_id = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    call_count = Column(Integer, default=0)
    kwh = Column(Float, default=0.0)
    water_l = Column(Float, default=0.0)
    co2_kg = Column(Float, default=0.0)


class DailyModelAgg(Base):
    __tablename__ = "daily_model_agg"

    date = Column(Date, primary_key=True)
    org_id = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    model = Column(String, primary_key=True)
    call_count = Column(Integer, default=0)
    kwh = Column(Float, default=0.0)
    water_l = Column(Float, default=0.0)
    co2_kg = Column(Float, default=0.0)
