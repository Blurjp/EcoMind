"""
Authentication and Authorization for EcoMind API

SCOPE (Codex Review P002):
This implementation focuses on CORE SECURITY ONLY:
- JWT token verification (no refresh tokens - deferred to Phase 2.5)
- RBAC enforcement with 5 roles
- Basic audit logging
- Password hashing with bcrypt

DEFERRED to later phases:
- Refresh token rotation (Codex concern: undefined storage/revocation)
- API key management (Codex concern: scope too large)
- Advanced rate limiting (Codex concern: infrastructure undefined)
- Account lockout (Codex concern: missing datastore)

Reference: phases/P002/codex_review.md:112
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User, Role
from app.models.audit import AuditLog

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token extraction
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload to encode (should include user_id, org_id, role)
        expires_delta: Token expiration time (default: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token from Authorization header.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return payload

    except JWTError:
        raise credentials_exception


async def get_current_user(
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database.

    Args:
        token_payload: Decoded JWT payload
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user not found
    """
    user_id = token_payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def require_role(*allowed_roles: Role):
    """
    Create a dependency that requires specific roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(Role.ADMIN, Role.OWNER))):
            ...

    Args:
        *allowed_roles: Roles that are allowed access

    Returns:
        Dependency function that checks role
    """
    async def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return check_role


async def require_same_org(
    org_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that user belongs to the specified organization.

    Args:
        org_id: Organization ID being accessed
        current_user: Currently authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: If user doesn't belong to org
    """
    if current_user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not belong to this organization"
        )

    return current_user


async def log_auth_event(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True
):
    """
    Log authentication/authorization events to audit_logs table.

    Args:
        db: Database session
        action: Action performed (e.g., "login", "logout", "access_denied")
        user_id: User ID (if known)
        org_id: Organization ID (if known)
        details: Additional details as JSON
        success: Whether the action succeeded
    """
    try:
        audit_log = AuditLog(
            org_id=org_id or "system",
            user_id=user_id,
            action=action,
            resource="authentication",
            details={
                **(details or {}),
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        # Don't fail the request if audit logging fails
        print(f"ERROR: Failed to log auth event: {e}")
        db.rollback()


# Permission helpers for RBAC

ROLE_PERMISSIONS = {
    Role.OWNER: {
        "read_own_data": True,
        "read_org_data": True,
        "write_data": True,
        "manage_users": True,
        "manage_billing": True,
        "manage_settings": True,
    },
    Role.ADMIN: {
        "read_own_data": True,
        "read_org_data": True,
        "write_data": True,
        "manage_users": True,
        "manage_billing": False,
        "manage_settings": True,
    },
    Role.ANALYST: {
        "read_own_data": True,
        "read_org_data": True,
        "write_data": False,
        "manage_users": False,
        "manage_billing": False,
        "manage_settings": False,
    },
    Role.VIEWER: {
        "read_own_data": True,
        "read_org_data": False,
        "write_data": False,
        "manage_users": False,
        "manage_billing": False,
        "manage_settings": False,
    },
    Role.BILLING: {
        "read_own_data": True,
        "read_org_data": True,  # For billing reports
        "write_data": False,
        "manage_users": False,
        "manage_billing": True,
        "manage_settings": False,
    },
}


def can_access_resource(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission based on their role.

    Args:
        user: User object
        permission: Permission name (e.g., "read_org_data")

    Returns:
        True if user has permission, False otherwise
    """
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    return role_perms.get(permission, False)


async def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission.

    Usage:
        @router.get("/org-data")
        async def get_org_data(user: User = Depends(require_permission("read_org_data"))):
            ...

    Args:
        permission: Permission name required

    Returns:
        Dependency function that checks permission
    """
    async def check_permission(current_user: User = Depends(get_current_user)):
        if not can_access_resource(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user

    return check_permission
