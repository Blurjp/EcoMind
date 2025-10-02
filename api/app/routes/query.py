from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models import DailyOrgAgg, DailyUserAgg, DailyProviderAgg, DailyModelAgg

router = APIRouter()


@router.get("/today")
async def get_today(
    org_id: str = Query(..., description="Organization ID"),
    user_id: Optional[str] = Query(None, description="User ID (optional)"),
    db: Session = Depends(get_db),
):
    """Get today's aggregated usage"""
    today = date.today()

    if user_id:
        # Query user aggregates
        agg = db.query(DailyUserAgg).filter(
            DailyUserAgg.date == today,
            DailyUserAgg.org_id == org_id,
            DailyUserAgg.user_id == user_id,
        ).first()

        if not agg:
            return {
                "date": today.isoformat(),
                "org_id": org_id,
                "user_id": user_id,
                "call_count": 0,
                "kwh": 0.0,
                "water_liters": 0.0,
                "co2_kg": 0.0,
                "top_providers": [],
                "top_models": [],
            }

        # Get top providers for this user today
        top_providers = db.query(
            DailyProviderAgg.provider,
            DailyProviderAgg.call_count
        ).filter(
            DailyProviderAgg.date == today,
            DailyProviderAgg.org_id == org_id,
        ).order_by(DailyProviderAgg.call_count.desc()).limit(5).all()

        # Get top models
        top_models = db.query(
            DailyModelAgg.model,
            DailyModelAgg.call_count
        ).filter(
            DailyModelAgg.date == today,
            DailyModelAgg.org_id == org_id,
        ).order_by(DailyModelAgg.call_count.desc()).limit(5).all()

        return {
            "date": today.isoformat(),
            "org_id": org_id,
            "user_id": user_id,
            "call_count": agg.call_count,
            "kwh": agg.kwh,
            "water_liters": agg.water_l,
            "co2_kg": agg.co2_kg,
            "top_providers": [{"provider": p, "count": c} for p, c in top_providers],
            "top_models": [{"model": m, "count": c} for m, c in top_models],
        }
    else:
        # Query org aggregates
        agg = db.query(DailyOrgAgg).filter(
            DailyOrgAgg.date == today,
            DailyOrgAgg.org_id == org_id,
        ).first()

        if not agg:
            return {
                "date": today.isoformat(),
                "org_id": org_id,
                "call_count": 0,
                "kwh": 0.0,
                "water_liters": 0.0,
                "co2_kg": 0.0,
                "top_providers": [],
                "top_models": [],
            }

        # Get top providers
        top_providers = db.query(
            DailyProviderAgg.provider,
            DailyProviderAgg.call_count
        ).filter(
            DailyProviderAgg.date == today,
            DailyProviderAgg.org_id == org_id,
        ).order_by(DailyProviderAgg.call_count.desc()).limit(5).all()

        # Get top models
        top_models = db.query(
            DailyModelAgg.model,
            DailyModelAgg.call_count
        ).filter(
            DailyModelAgg.date == today,
            DailyModelAgg.org_id == org_id,
        ).order_by(DailyModelAgg.call_count.desc()).limit(5).all()

        return {
            "date": today.isoformat(),
            "org_id": org_id,
            "call_count": agg.call_count,
            "kwh": agg.kwh,
            "water_liters": agg.water_l,
            "co2_kg": agg.co2_kg,
            "top_providers": [{"provider": p, "count": c} for p, c in top_providers],
            "top_models": [{"model": m, "count": c} for m, c in top_models],
        }


@router.get("/aggregate/daily")
async def get_daily_aggregate(
    org_id: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    group_by: str = Query("provider", regex="^(provider|model|user)$"),
    db: Session = Depends(get_db),
):
    """Get daily aggregates with grouping"""
    from_dt = date.fromisoformat(from_date)
    to_dt = date.fromisoformat(to_date)

    if group_by == "provider":
        results = db.query(
            DailyProviderAgg.date,
            DailyProviderAgg.provider,
            func.sum(DailyProviderAgg.call_count).label("call_count"),
            func.sum(DailyProviderAgg.kwh).label("kwh"),
            func.sum(DailyProviderAgg.water_l).label("water_l"),
            func.sum(DailyProviderAgg.co2_kg).label("co2_kg"),
        ).filter(
            DailyProviderAgg.org_id == org_id,
            DailyProviderAgg.date >= from_dt,
            DailyProviderAgg.date <= to_dt,
        ).group_by(DailyProviderAgg.date, DailyProviderAgg.provider).all()

        return {
            "org_id": org_id,
            "from": from_date,
            "to": to_date,
            "group_by": group_by,
            "data": [
                {
                    "date": r.date.isoformat(),
                    "provider": r.provider,
                    "call_count": r.call_count,
                    "kwh": r.kwh,
                    "water_liters": r.water_l,
                    "co2_kg": r.co2_kg,
                }
                for r in results
            ],
        }

    elif group_by == "model":
        results = db.query(
            DailyModelAgg.date,
            DailyModelAgg.provider,
            DailyModelAgg.model,
            func.sum(DailyModelAgg.call_count).label("call_count"),
            func.sum(DailyModelAgg.kwh).label("kwh"),
            func.sum(DailyModelAgg.water_l).label("water_l"),
            func.sum(DailyModelAgg.co2_kg).label("co2_kg"),
        ).filter(
            DailyModelAgg.org_id == org_id,
            DailyModelAgg.date >= from_dt,
            DailyModelAgg.date <= to_dt,
        ).group_by(
            DailyModelAgg.date,
            DailyModelAgg.provider,
            DailyModelAgg.model
        ).all()

        return {
            "org_id": org_id,
            "from": from_date,
            "to": to_date,
            "group_by": group_by,
            "data": [
                {
                    "date": r.date.isoformat(),
                    "provider": r.provider,
                    "model": r.model,
                    "call_count": r.call_count,
                    "kwh": r.kwh,
                    "water_liters": r.water_l,
                    "co2_kg": r.co2_kg,
                }
                for r in results
            ],
        }

    else:  # user
        results = db.query(
            DailyUserAgg.date,
            DailyUserAgg.user_id,
            func.sum(DailyUserAgg.call_count).label("call_count"),
            func.sum(DailyUserAgg.kwh).label("kwh"),
            func.sum(DailyUserAgg.water_l).label("water_l"),
            func.sum(DailyUserAgg.co2_kg).label("co2_kg"),
        ).filter(
            DailyUserAgg.org_id == org_id,
            DailyUserAgg.date >= from_dt,
            DailyUserAgg.date <= to_dt,
        ).group_by(DailyUserAgg.date, DailyUserAgg.user_id).all()

        return {
            "org_id": org_id,
            "from": from_date,
            "to": to_date,
            "group_by": group_by,
            "data": [
                {
                    "date": r.date.isoformat(),
                    "user_id": r.user_id,
                    "call_count": r.call_count,
                    "kwh": r.kwh,
                    "water_liters": r.water_l,
                    "co2_kg": r.co2_kg,
                }
                for r in results
            ],
        }