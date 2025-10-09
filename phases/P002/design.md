# Phase 2: Authentication & Authorization Enforcement

**Phase ID**: P002
**Duration**: 1 week (5 business days)
**Priority**: HIGH (SECURITY CRITICAL)
**Owner**: Backend Team
**Status**: Design Review
**Dependencies**: P001 (requires audit_logs table)

---

## 1. Executive Summary

Implement comprehensive JWT-based authentication and RBAC (Role-Based Access Control) enforcement across all API endpoints to secure enterprise telemetry data and prevent unauthorized access.

**Problem Statement:**
- **CRITICAL SECURITY VULNERABILITY**: API routes have no authentication (`api/app/routes/query.py`)
- Any client can query any organization's data without credentials
- No authorization checks (RBAC roles defined but not enforced)
- No audit logging for security events
- JWT validation stubs exist (`api/app/auth.py`) but not applied to routes

**Success Criteria:**
- ✅ All API endpoints require valid JWT tokens
- ✅ RBAC roles enforced (Owner/Admin/Analyst/Viewer/Billing)
- ✅ Audit logging for all authentication/authorization events
- ✅ Rate limiting per user/org
- ✅ Security tests passing (penetration testing)
- ✅ Zero unauthorized access in production

---

## 2. Technical Architecture

### 2.1 Current State Analysis

**Evidence from codebase:**

**File**: `api/app/routes/query.py:14-19`
```python
@router.get("/today")
async def get_today(
    org_id: str = Query(..., description="Organization ID"),
    user_id: Optional[str] = Query(None, description="User ID (optional)"),
    db: Session = Depends(get_db),
):
    """Get today's aggregated usage"""
```

**CRITICAL ISSUE**: No `current_user: User = Depends(verify_token)` dependency!

**File**: `api/app/auth.py` (referenced in `ENTERPRISE_SETUP.md:492-503`)
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials):
    # Validate JWT token
    # Check org_id scope
    # Return user context
```

**Status**: Stub exists but NOT used in any route handlers.

**File**: `api/app/models/user.py` (referenced in `ENTERPRISE_SETUP.md:512-530`)
```python
# Roles defined:
# - Owner: Full access, billing
# - Admin: User management, settings
# - Analyst: Read all data, export
# - Viewer: Read own data only
# - Billing: Invoices, usage reports
```

**Status**: Roles defined but not enforced in route logic.

### 2.2 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   API Request Flow                          │
└─────────────────────────────────────────────────────────────┘

1. Client Request
   ↓
2. Middleware: CORS, Rate Limiting
   ↓
3. HTTPBearer: Extract JWT from Authorization header
   ↓
4. verify_token(): Validate JWT signature, expiration
   ↓
5. load_user(): Fetch user from database (with org context)
   ↓
6. check_permission(): Verify RBAC role for resource
   ↓
7. Route Handler: Execute business logic
   ↓
8. audit_log(): Record security event
   ↓
9. Response
```

**Components:**

```
api/
├── app/
│   ├── auth/                          # NEW: Auth module
│   │   ├── __init__.py
│   │   ├── jwt.py                     # JWT encoding/decoding
│   │   ├── dependencies.py            # FastAPI dependencies
│   │   ├── permissions.py             # RBAC checks
│   │   └── middleware.py              # Rate limiting, CORS
│   ├── models/
│   │   ├── user.py                    # UPDATED: Add password hash
│   │   ├── api_key.py                 # NEW: API key model
│   │   └── refresh_token.py           # NEW: Refresh token model
│   ├── routes/
│   │   ├── auth.py                    # NEW: Login, logout, refresh
│   │   ├── query.py                   # UPDATED: Add auth dependencies
│   │   ├── orgs.py                    # UPDATED: Add auth dependencies
│   │   └── users.py                   # UPDATED: Add auth dependencies
│   └── utils/
│       └── audit.py                   # NEW: Audit logging helper
├── tests/
│   ├── test_auth.py                   # NEW: Auth tests
│   └── test_permissions.py            # NEW: RBAC tests
└── .env.example                       # UPDATED: Add JWT_SECRET
```

### 2.3 JWT Token Design

**Token Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_alice",                // User ID
    "org_id": "org_acme",               // Organization ID
    "role": "admin",                    // RBAC role
    "email": "alice@acme.com",
    "iat": 1696684800,                  // Issued at
    "exp": 1696688400,                  // Expires (1 hour)
    "jti": "unique-token-id"            // JWT ID (for revocation)
  },
  "signature": "..."
}
```

**Token Lifetimes:**
- Access token: 1 hour (short-lived)
- Refresh token: 30 days (stored in database, revocable)
- API key: 1 year (for service-to-service)

**Security Features:**
- HS256 signature algorithm (symmetric, fast)
- JWT secret rotation every 90 days
- Token revocation via database (blacklist)
- Rate limiting: 100 requests/min per user

### 2.4 RBAC Permission Matrix

| Resource | Owner | Admin | Analyst | Viewer | Billing |
|----------|-------|-------|---------|--------|---------|
| **Organizations** |
| Create org | ✅ | ❌ | ❌ | ❌ | ❌ |
| Read org | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update org | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete org | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Users** |
| Create user | ✅ | ✅ | ❌ | ❌ | ❌ |
| Read users | ✅ | ✅ | ✅ | Self only | ✅ |
| Update user | ✅ | ✅ | Self only | Self only | Self only |
| Delete user | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Events** |
| Ingest event | ✅ | ✅ | ✅ | ✅ | ❌ |
| Read events | ✅ | ✅ | ✅ | Self only | ✅ |
| Export events | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Aggregates** |
| Read org agg | ✅ | ✅ | ✅ | ❌ | ✅ |
| Read user agg | ✅ | ✅ | ✅ | Self only | ✅ |
| **Alerts** |
| Create alert | ✅ | ✅ | ❌ | ❌ | ❌ |
| Read alerts | ✅ | ✅ | ✅ | ❌ | ❌ |
| Update alert | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete alert | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Reports** |
| Generate report | ✅ | ✅ | ✅ | ❌ | ✅ |
| Download report | ✅ | ✅ | ✅ | Self only | ✅ |
| **Audit Logs** |
| Read audit logs | ✅ | ✅ | ❌ | ❌ | ❌ |

**Permission Check Logic:**
```python
def check_permission(user: User, resource: str, action: str, resource_org_id: str = None) -> bool:
    # Check org membership
    if resource_org_id and user.org_id != resource_org_id:
        raise HTTPException(403, "Access denied: not a member of this organization")

    # Check role permissions
    permissions = PERMISSION_MATRIX[user.role]
    if (resource, action) not in permissions:
        raise HTTPException(403, f"Access denied: {user.role} cannot {action} {resource}")

    return True
```

---

## 3. Implementation Plan

### 3.1 Day 1: JWT Implementation

**Tasks:**

1. Install dependencies
   ```bash
   cd api
   pip install python-jose[cryptography] passlib[bcrypt] python-multipart
   ```

2. Create `app/auth/jwt.py`
   ```python
   from datetime import datetime, timedelta
   from jose import JWTError, jwt
   from passlib.context import CryptContext
   import os

   SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = 60

   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

   def create_access_token(data: dict, expires_delta: timedelta = None):
       to_encode = data.copy()
       if expires_delta:
           expire = datetime.utcnow() + expires_delta
       else:
           expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
       to_encode.update({"exp": expire})
       encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
       return encoded_jwt

   def verify_token(token: str):
       try:
           payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
           user_id: str = payload.get("sub")
           if user_id is None:
               raise HTTPException(401, "Invalid token")
           return payload
       except JWTError:
           raise HTTPException(401, "Invalid token")

   def hash_password(password: str):
       return pwd_context.hash(password)

   def verify_password(plain_password: str, hashed_password: str):
       return pwd_context.verify(plain_password, hashed_password)
   ```

3. Update `app/models/user.py`
   ```python
   from sqlalchemy import Column, String, DateTime, Enum
   from app.db import Base
   import enum

   class UserRole(str, enum.Enum):
       OWNER = "owner"
       ADMIN = "admin"
       ANALYST = "analyst"
       VIEWER = "viewer"
       BILLING = "billing"

   class User(Base):
       __tablename__ = "users"

       user_id = Column(String(255), primary_key=True)
       org_id = Column(String(255), nullable=False)
       email = Column(String(255), unique=True, nullable=False)
       password_hash = Column(String(255), nullable=False)  # NEW
       role = Column(Enum(UserRole), default=UserRole.VIEWER)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

4. Create migration for password_hash
   ```bash
   alembic revision -m "Add password_hash to users"
   ```

**Deliverables:**
- ✅ JWT encoding/decoding working
- ✅ Password hashing implemented
- ✅ User model updated

### 3.2 Day 2: Authentication Routes

**Tasks:**

1. Create `app/routes/auth.py`
   ```python
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from app.db import get_db
   from app.models.user import User
   from app.auth.jwt import create_access_token, verify_password
   from pydantic import BaseModel

   router = APIRouter()

   class LoginRequest(BaseModel):
       email: str
       password: str

   class LoginResponse(BaseModel):
       access_token: str
       token_type: str = "bearer"
       user_id: str
       org_id: str
       role: str

   @router.post("/login", response_model=LoginResponse)
   async def login(request: LoginRequest, db: Session = Depends(get_db)):
       user = db.query(User).filter(User.email == request.email).first()
       if not user or not verify_password(request.password, user.password_hash):
           raise HTTPException(401, "Invalid credentials")

       token_data = {
           "sub": user.user_id,
           "org_id": user.org_id,
           "role": user.role,
           "email": user.email,
       }
       access_token = create_access_token(token_data)

       # Audit log
       audit_log(db, user.org_id, user.user_id, "auth.login", None, None, request.client.host)

       return LoginResponse(
           access_token=access_token,
           user_id=user.user_id,
           org_id=user.org_id,
           role=user.role,
       )

   @router.post("/logout")
   async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
       # Revoke token (add to blacklist or delete refresh token)
       audit_log(db, current_user.org_id, current_user.user_id, "auth.logout", None, None, None)
       return {"message": "Logged out successfully"}
   ```

2. Create `app/auth/dependencies.py`
   ```python
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   from sqlalchemy.orm import Session
   from app.db import get_db
   from app.models.user import User
   from app.auth.jwt import verify_token

   security = HTTPBearer()

   async def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: Session = Depends(get_db)
   ) -> User:
       payload = verify_token(credentials.credentials)
       user_id = payload.get("sub")
       user = db.query(User).filter(User.user_id == user_id).first()
       if not user:
           raise HTTPException(401, "User not found")
       return user
   ```

**Deliverables:**
- ✅ Login endpoint working
- ✅ Logout endpoint working
- ✅ `get_current_user` dependency ready

### 3.3 Day 3: RBAC Enforcement

**Tasks:**

1. Create `app/auth/permissions.py`
   ```python
   from fastapi import HTTPException
   from app.models.user import User, UserRole
   from typing import List

   PERMISSION_MATRIX = {
       UserRole.OWNER: {
           "org": ["create", "read", "update", "delete"],
           "user": ["create", "read", "update", "delete"],
           "event": ["ingest", "read", "export"],
           "aggregate": ["read"],
           "alert": ["create", "read", "update", "delete"],
           "report": ["generate", "download"],
           "audit": ["read"],
       },
       UserRole.ADMIN: {
           "org": ["read", "update"],
           "user": ["create", "read", "update", "delete"],
           "event": ["ingest", "read", "export"],
           "aggregate": ["read"],
           "alert": ["create", "read", "update", "delete"],
           "report": ["generate", "download"],
           "audit": ["read"],
       },
       UserRole.ANALYST: {
           "org": ["read"],
           "user": ["read"],
           "event": ["ingest", "read", "export"],
           "aggregate": ["read"],
           "alert": ["read"],
           "report": ["generate", "download"],
       },
       UserRole.VIEWER: {
           "org": ["read"],
           "event": ["ingest", "read"],
           "aggregate": ["read_own"],
       },
       UserRole.BILLING: {
           "org": ["read"],
           "user": ["read"],
           "event": ["read"],
           "aggregate": ["read"],
           "report": ["generate", "download"],
       },
   }

   def require_permission(resource: str, action: str):
       def decorator(current_user: User = Depends(get_current_user)):
           permissions = PERMISSION_MATRIX.get(current_user.role, {})
           allowed_actions = permissions.get(resource, [])
           if action not in allowed_actions:
               raise HTTPException(403, f"Access denied: {current_user.role} cannot {action} {resource}")
           return current_user
       return decorator

   def require_org_access(resource_org_id: str, current_user: User = Depends(get_current_user)):
       if current_user.org_id != resource_org_id:
           raise HTTPException(403, "Access denied: not a member of this organization")
       return current_user
   ```

2. Update `app/routes/query.py`
   ```python
   from app.auth.dependencies import get_current_user
   from app.auth.permissions import require_permission, require_org_access
   from app.models.user import User

   @router.get("/today")
   async def get_today(
       org_id: str = Query(...),
       user_id: Optional[str] = Query(None),
       current_user: User = Depends(get_current_user),  # NEW: Require auth
       db: Session = Depends(get_db),
   ):
       # NEW: Check org membership
       if current_user.org_id != org_id:
           raise HTTPException(403, "Access denied")

       # NEW: Check permission
       if user_id and current_user.role == UserRole.VIEWER:
           # Viewer can only see own data
           if user_id != current_user.user_id:
               raise HTTPException(403, "Viewers can only access their own data")

       # Original logic...
   ```

3. Update all routes in `api/app/routes/`
   - `orgs.py`: Add `get_current_user` to all endpoints
   - `users.py`: Add RBAC checks for user management
   - `alerts.py`: Add RBAC checks for alert management
   - `reports.py`: Add RBAC checks for report generation

**Deliverables:**
- ✅ RBAC permission matrix implemented
- ✅ All routes protected with auth

### 3.4 Day 4: Audit Logging & Rate Limiting

**Tasks:**

1. Create `app/utils/audit.py`
   ```python
   from sqlalchemy.orm import Session
   from app.models.audit import AuditLog
   from datetime import datetime

   def audit_log(
       db: Session,
       org_id: str,
       user_id: str,
       action: str,
       resource_type: str = None,
       resource_id: str = None,
       ip_address: str = None,
       metadata: dict = None,
   ):
       log = AuditLog(
           org_id=org_id,
           user_id=user_id,
           action=action,
           resource_type=resource_type,
           resource_id=resource_id,
           ip_address=ip_address,
           metadata=metadata,
           timestamp=datetime.utcnow(),
       )
       db.add(log)
       db.commit()
   ```

2. Create `app/auth/middleware.py`
   ```python
   from fastapi import Request, HTTPException
   from starlette.middleware.base import BaseHTTPMiddleware
   import redis
   import os

   redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

   class RateLimitMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request: Request, call_next):
           # Get user ID from token (if present)
           auth_header = request.headers.get("Authorization")
           if auth_header:
               token = auth_header.replace("Bearer ", "")
               payload = verify_token(token)
               user_id = payload.get("sub")

               # Rate limit: 100 requests per minute per user
               key = f"ratelimit:{user_id}"
               count = redis_client.incr(key)
               if count == 1:
                   redis_client.expire(key, 60)
               if count > 100:
                   raise HTTPException(429, "Rate limit exceeded")

           response = await call_next(request)
           return response
   ```

3. Update `app/main.py`
   ```python
   from app.auth.middleware import RateLimitMiddleware

   app.add_middleware(RateLimitMiddleware)
   ```

**Deliverables:**
- ✅ Audit logging working
- ✅ Rate limiting implemented

### 3.5 Day 5: Testing & Documentation

**Tasks:**

1. Create `tests/test_auth.py`
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app

   client = TestClient(app)

   def test_login_success():
       response = client.post("/v1/auth/login", json={
           "email": "alice@acme.com",
           "password": "password123",
       })
       assert response.status_code == 200
       assert "access_token" in response.json()

   def test_login_invalid_credentials():
       response = client.post("/v1/auth/login", json={
           "email": "alice@acme.com",
           "password": "wrong",
       })
       assert response.status_code == 401

   def test_protected_route_without_token():
       response = client.get("/v1/today?org_id=org_acme")
       assert response.status_code == 401

   def test_protected_route_with_token():
       # Login first
       login_response = client.post("/v1/auth/login", json={
           "email": "alice@acme.com",
           "password": "password123",
       })
       token = login_response.json()["access_token"]

       # Access protected route
       response = client.get(
           "/v1/today?org_id=org_acme",
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 200
   ```

2. Create `tests/test_permissions.py`
   ```python
   def test_viewer_cannot_read_org_data():
       token = login_as("viewer@acme.com", "password")
       response = client.get(
           "/v1/today?org_id=org_acme",
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 403

   def test_admin_can_create_user():
       token = login_as("admin@acme.com", "password")
       response = client.post(
           "/v1/users",
           json={"email": "newuser@acme.com", "role": "viewer"},
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 201

   def test_viewer_cannot_create_user():
       token = login_as("viewer@acme.com", "password")
       response = client.post(
           "/v1/users",
           json={"email": "newuser@acme.com", "role": "viewer"},
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 403
   ```

3. Create `docs/AUTHENTICATION.md`
   - How to obtain JWT tokens
   - API authentication examples
   - RBAC role descriptions
   - Rate limiting policies
   - Security best practices

4. Update `README.md` with auth setup instructions

**Deliverables:**
- ✅ Auth tests passing
- ✅ Permission tests passing
- ✅ Documentation complete

---

## 4. Risk Analysis

### 4.1 High Risks

**Risk 1: JWT Secret Compromise**
- **Likelihood**: Low
- **Impact**: Critical (full system compromise)
- **Mitigation**:
  - Store JWT_SECRET in environment variables (never in code)
  - Rotate secret every 90 days
  - Use strong random secret (32+ bytes)
  - Implement token revocation

**Risk 2: Broken Access Control**
- **Likelihood**: Medium
- **Impact**: High (data breach)
- **Mitigation**:
  - Comprehensive permission tests for all roles
  - Penetration testing before production
  - Security audit by external team
  - Real-time monitoring of failed auth attempts

### 4.2 Medium Risks

**Risk 3: Rate Limiting Bypass**
- **Likelihood**: Medium
- **Impact**: Medium (DDoS)
- **Mitigation**:
  - Multiple rate limiting layers (user, IP, org)
  - CloudFlare/WAF in front of API
  - Monitor for unusual traffic patterns

**Risk 4: Password Brute Force**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - bcrypt with high cost factor (12+)
  - Account lockout after 5 failed attempts
  - CAPTCHA for suspicious login patterns
  - Alert on multiple failed logins

---

## 5. Success Metrics

**Quantitative:**
- ✅ 0 unauthorized access attempts succeed
- ✅ 100% of endpoints require authentication
- ✅ < 100ms auth overhead per request
- ✅ 0 security incidents in first 30 days

**Qualitative:**
- ✅ Enterprises trust the security model
- ✅ Compliance with SOC2/GDPR requirements
- ✅ Security audit passes with no critical findings

---

## 6. Dependencies

**Upstream (Blockers):**
- P001: Database Migrations (needs audit_logs table)

**Downstream (Dependent on this):**
- P003: Infrastructure-as-Code (needs secure deployment)
- P004: Monitoring (needs auth metrics)

---

## 7. Open Questions

1. **OAuth2 Support**: Should we support SSO (Google, GitHub)?
   - **Recommendation**: Add in P002.5 (after basic JWT working)

2. **API Key Management**: How do users generate/revoke API keys?
   - **Recommendation**: Admin UI in Phase 4 (dashboard)

3. **Token Refresh Strategy**: Automatic refresh or require re-login?
   - **Recommendation**: Refresh tokens with 30-day expiry

---

## 8. References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- Internal: `api/app/routes/query.py` (current vulnerable endpoints)

---

## 9. Acceptance Criteria

- [ ] JWT encoding/decoding implemented
- [ ] Login/logout endpoints working
- [ ] `get_current_user` dependency enforced on all routes
- [ ] RBAC permission matrix implemented
- [ ] Audit logging for all auth events
- [ ] Rate limiting (100 req/min per user)
- [ ] Password hashing with bcrypt
- [ ] 20+ auth/permission tests passing
- [ ] Documentation complete (`AUTHENTICATION.md`)
- [ ] Penetration testing reveals no critical vulnerabilities
- [ ] Zero unauthorized access in staging environment test

---

**Design Status**: Ready for Codex Review
**Next Step**: Codex review → Implementation → Security testing → Production deployment
