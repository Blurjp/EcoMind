"""
Authentication routes for EcoMind API

SCOPE (Codex Review P002):
- Login/Logout only (no refresh token endpoints)
- Basic audit logging
- Password-based authentication

DEFERRED to Phase 2.5:
- Refresh token rotation
- Password reset
- Email verification
- OAuth/OIDC integration

Reference: phases/P002/codex_review.md:112
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User, Role
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    log_auth_event,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


# Request/Response models

class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RegisterRequest(BaseModel):
    """User registration request.

    Note: Role is NOT accepted from client payload for security.
    Only authenticated ADMIN/OWNER users can specify roles via admin endpoints.
    """
    email: EmailStr
    password: str
    name: str
    org_id: str


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    name: Optional[str]
    org_id: str
    role: str

    class Config:
        from_attributes = True


# Routes

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.

    This endpoint:
    1. Validates email/password
    2. Creates JWT token
    3. Logs authentication event to audit_logs

    Args:
        credentials: Email and password
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: 401 if credentials invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not user.password_hash:
        await log_auth_event(
            db,
            action="login_failed",
            details={"email": credentials.email, "reason": "user_not_found"},
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        await log_auth_event(
            db,
            action="login_failed",
            user_id=user.id,
            org_id=user.org_id,
            details={"email": credentials.email, "reason": "invalid_password"},
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "org_id": user.org_id,
            "role": user.role.value
        }
    )

    # Log successful login
    await log_auth_event(
        db,
        action="login_success",
        user_id=user.id,
        org_id=user.org_id,
        details={"email": credentials.email},
        success=True
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "org_id": user.org_id,
            "role": user.role.value
        }
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user.

    Note: With stateless JWT tokens, logout is primarily client-side
    (client discards token). This endpoint logs the event for audit purposes.

    For token revocation (blocking compromised tokens), use Phase 2.5
    refresh token rotation or a token blacklist (requires Redis).

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Success message
    """
    await log_auth_event(
        db,
        action="logout",
        user_id=current_user.id,
        org_id=current_user.org_id,
        details={"email": current_user.email},
        success=True
    )

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Currently authenticated user

    Returns:
        User information
    """
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new user (ADMIN/OWNER only).

    SECURITY (Codex Review):
    - Requires authentication (prevents anonymous account creation)
    - Requires ADMIN or OWNER role (only privileged users can create accounts)
    - Role is ALWAYS set to VIEWER (clients cannot self-select elevated roles)
    - Validates org_id exists before creation (prevents FK integrity errors)

    For self-service registration, implement a separate public endpoint with:
    - Email verification workflow
    - Rate limiting
    - Organization invitation tokens
    - Automatic VIEWER role assignment

    Args:
        user_data: User registration data
        db: Database session
        current_user: Currently authenticated user (must be ADMIN/OWNER)

    Returns:
        Created user information

    Raises:
        HTTPException: 403 if caller lacks permissions
        HTTPException: 400 if email already exists
        HTTPException: 404 if organization not found
    """
    # SECURITY: Require ADMIN or OWNER role to create users
    from app.auth import can_access_resource
    if not can_access_resource(current_user, "manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN or OWNER users can create new accounts"
        )

    # SECURITY: Validate that caller belongs to the target organization
    if current_user.org_id != user_data.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create users in your own organization"
        )

    # Validate organization exists (prevents FK integrity error)
    from app.models.org import Org
    org = db.query(Org).filter(Org.id == user_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{user_data.org_id}' not found"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # SECURITY: Always create users as VIEWER (no self-selected roles)
    # For role elevation, use separate admin endpoint
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        org_id=user_data.org_id,
        password_hash=hash_password(user_data.password),
        role=Role.VIEWER  # Hardcoded - cannot be influenced by client
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    await log_auth_event(
        db,
        action="user_registered",
        user_id=new_user.id,
        org_id=new_user.org_id,
        details={
            "email": new_user.email,
            "role": new_user.role.value,
            "created_by": current_user.id
        },
        success=True
    )

    return new_user
