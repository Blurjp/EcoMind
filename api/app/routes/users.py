from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db import get_db
from app.models import User, Role

router = APIRouter()


class UserCreate(BaseModel):
    org_id: str
    email: EmailStr
    name: str
    role: Role = Role.VIEWER


class UserResponse(BaseModel):
    id: str
    org_id: str
    email: str
    name: str
    role: Role
    created_at: str

    class Config:
        from_attributes = True


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        org_id=user.org_id,
        email=user.email,
        name=user.name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/orgs/{org_id}/users", response_model=list[UserResponse])
async def list_org_users(org_id: str, db: Session = Depends(get_db)):
    """List users in an organization"""
    users = db.query(User).filter(User.org_id == org_id).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
