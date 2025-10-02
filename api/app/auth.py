"""
Minimal auth/RBAC placeholders.
Full implementation would include JWT middleware, OIDC/SAML, API keys, etc.
"""

from typing import Optional
from fastapi import Header, HTTPException


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Placeholder for JWT/API key validation.
    Returns user context: org_id, user_id, role.
    """
    # TODO: Validate JWT or API key
    # For now, return demo user
    if not authorization:
        # Allow unauthenticated for development
        return {
            "org_id": "org_demo",
            "user_id": "user_alice",
            "role": "admin",
        }

    # Parse Bearer token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        # TODO: Verify JWT
        return {
            "org_id": "org_demo",
            "user_id": "user_alice",
            "role": "admin",
        }

    raise HTTPException(status_code=401, detail="Invalid authorization")


def require_role(*roles: str):
    """
    Dependency to enforce RBAC.
    Usage: Depends(require_role("admin", "owner"))
    """
    async def check_role(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check_role
