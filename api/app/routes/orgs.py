from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models import Org, PlanType

router = APIRouter()


class OrgCreate(BaseModel):
    name: str
    plan: PlanType = PlanType.FREE


class OrgResponse(BaseModel):
    id: str
    name: str
    plan: PlanType
    created_at: str

    class Config:
        from_attributes = True


@router.post("/orgs", response_model=OrgResponse)
async def create_org(org: OrgCreate, db: Session = Depends(get_db)):
    """Create a new organization"""
    db_org = Org(name=org.name, plan=org.plan)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


@router.get("/orgs/{org_id}", response_model=OrgResponse)
async def get_org(org_id: str, db: Session = Depends(get_db)):
    """Get organization by ID"""
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/orgs", response_model=list[OrgResponse])
async def list_orgs(db: Session = Depends(get_db)):
    """List all organizations"""
    orgs = db.query(Org).all()
    return orgs
