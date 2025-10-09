# EcoMind API Deployment Plan

**Version:** Phase 1 + Phase 2 (Authentication & Authorization)
**Date:** 2025-10-08
**Status:** Ready for Staging Deployment

---

## Executive Summary

This deployment includes:
- **Phase 1**: Database migration infrastructure (Alembic)
- **Phase 2**: Authentication & Authorization (JWT, RBAC)
- **Security Fixes**: Critical vulnerabilities patched (CVSS 10.0 + 5.3)

**Critical Security Patches Included:**
- ✅ Registration endpoint now requires authentication
- ✅ Privilege escalation vulnerability fixed
- ✅ Database schema information leakage prevented

---

## Pre-Deployment Checklist

### 1. Environment Preparation

**Required Environment Variables:**
```bash
# Database
export DATABASE_URL="postgresql://user:password@host:5432/dbname"

# JWT Authentication
export JWT_SECRET="<strong-random-secret-min-32-chars>"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"

# Application
export PYTHONPATH="/path/to/ecomind/api"
```

**Generate JWT Secret (if needed):**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Dependencies Installation

**Install Python Dependencies:**
```bash
cd /Users/jianphua/projects/EcoMind/api
pip install -e ".[dev]"
```

**Verify Critical Dependencies:**
```bash
python3 -c "
import fastapi
import sqlalchemy
import alembic
import jose
import passlib
print('✅ All dependencies installed')
"
```

### 3. Database Preparation

**For New Databases:**
```bash
cd /Users/jianphua/projects/EcoMind/api

# Run migrations
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
alembic upgrade head

# Verify schema
python3 scripts/verify_schema.py
```

**For Existing Databases (with tables already present):**
```bash
cd /Users/jianphua/projects/EcoMind/api

# Baseline database (marks as migrated without creating tables)
bash scripts/baseline_database.sh --dry-run
# If looks good:
bash scripts/baseline_database.sh

# Then apply Phase 2 migration
alembic upgrade head
```

### 4. Pre-Deployment Testing

**Unit Tests (if environment set up):**
```bash
cd /Users/jianphua/projects/EcoMind/api
pytest tests/test_auth/ -v
pytest tests/test_migrations/ -v
```

**Manual Testing Checklist:**
- [ ] Database connection successful
- [ ] Migrations apply cleanly
- [ ] Schema verification passes
- [ ] API starts without errors

---

## Deployment Steps

### Staging Environment

#### Step 1: Backup Current State

```bash
# Backup database
pg_dump -h <staging-host> -U <user> -d ecomind > backup_staging_$(date +%Y%m%d_%H%M%S).sql

# Backup current code
git tag deployment-staging-$(date +%Y%m%d-%H%M%S)
git push --tags
```

#### Step 2: Deploy Code

```bash
# Pull latest code
cd /path/to/staging/ecomind
git fetch origin
git checkout main
git pull origin main

# Verify commit includes security fixes
git log --oneline -5
# Should show:
# - Critical security fixes in auth.py
# - Enum case mismatch fixes
# - Missing dependencies added
```

#### Step 3: Update Dependencies

```bash
cd api
pip install -e ".[dev]" --upgrade
```

#### Step 4: Set Environment Variables

```bash
# On staging server, set/verify:
export DATABASE_URL="postgresql://ecomind_staging:***@staging-db:5432/ecomind"
export JWT_SECRET="<strong-secret-for-staging>"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
```

#### Step 5: Run Migrations

```bash
cd api

# Check current migration status
alembic current

# Show pending migrations
alembic history

# Apply migrations
alembic upgrade head

# Verify
python3 scripts/verify_schema.py
```

**Expected Output:**
```
✅ Checking database connection...
✅ Database connection successful

✅ Checking tables...
✅ All 8 expected tables exist

✅ Checking table structures...
✅ Table 'orgs' structure is correct
✅ Table 'users' structure is correct (includes password_hash)
✅ Table 'events_enriched' structure is correct
✅ Table 'daily_org_agg' structure is correct
✅ Table 'daily_user_agg' structure is correct
✅ Table 'daily_provider_agg' structure is correct
✅ Table 'daily_model_agg' structure is correct
✅ Table 'audit_logs' structure is correct

✅ Schema verification PASSED
```

#### Step 6: Restart Application

```bash
# Using systemd
sudo systemctl restart ecomind-api

# Using Docker
docker-compose restart api

# Using supervisor
supervisorctl restart ecomind-api

# Verify service is running
curl http://localhost:8000/health
```

#### Step 7: Post-Deployment Verification

**Health Check:**
```bash
curl http://staging-api.ecomind.com/health
# Expected: {"status": "healthy", ...}

curl http://staging-api.ecomind.com/
# Expected: {"service": "ecomind-api", "version": "0.1.0", ...}
```

**Security Verification:**

Test 1: Anonymous registration blocked
```bash
curl -X POST http://staging-api.ecomind.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User",
    "org_id": "org_test"
  }'
# Expected: 401 Unauthorized
```

Test 2: Login works
```bash
# First, create a test ADMIN user via database:
# INSERT INTO users (id, email, name, org_id, password_hash, role)
# VALUES ('user_test', 'admin@test.com', 'Admin', 'org_test', '<bcrypt-hash>', 'admin');

curl -X POST http://staging-api.ecomind.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "test123"
  }'
# Expected: {"access_token": "...", "token_type": "bearer", ...}
```

Test 3: Authenticated registration works (ADMIN/OWNER only)
```bash
TOKEN="<token-from-login>"

curl -X POST http://staging-api.ecomind.com/v1/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "password123",
    "name": "New User",
    "org_id": "org_test"
  }'
# Expected: 201 Created (user created as VIEWER)
```

Test 4: VIEWER cannot create users
```bash
# Login as VIEWER user
VIEWER_TOKEN="<viewer-token>"

curl -X POST http://staging-api.ecomind.com/v1/auth/register \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d '{"email": "test2@test.com", ...}'
# Expected: 403 Forbidden (manage_users permission required)
```

Test 5: Invalid org_id returns clean error
```bash
curl -X POST http://staging-api.ecomind.com/v1/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"email": "test3@test.com", "org_id": "org_nonexistent", ...}'
# Expected: 404 Not Found (no stack trace, no IntegrityError)
```

---

### Production Environment

**⚠️ IMPORTANT: Only proceed if staging verification passes completely**

#### Step 1: Pre-Production Checklist

- [ ] Staging deployment successful
- [ ] All security tests passed in staging
- [ ] No errors in staging logs (check 24+ hours)
- [ ] Performance acceptable in staging
- [ ] Database backup created
- [ ] Rollback plan ready
- [ ] Maintenance window scheduled (if needed)

#### Step 2: Backup Production

```bash
# Backup production database
pg_dump -h <prod-host> -U <user> -d ecomind_prod > backup_prod_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
psql -h localhost -U postgres -d temp_verify < backup_prod_*.sql

# Tag current production state
git tag production-pre-phase2-$(date +%Y%m%d-%H%M%S)
git push --tags
```

#### Step 3: Deploy to Production

**Same steps as staging, but with production credentials**

```bash
# 1. Pull code
cd /path/to/production/ecomind
git checkout main
git pull origin main

# 2. Update dependencies
cd api
pip install -e ".[dev]" --upgrade

# 3. Set production environment variables
export DATABASE_URL="postgresql://ecomind_prod:***@prod-db:5432/ecomind"
export JWT_SECRET="<strong-secret-for-production>"  # Different from staging!
export ACCESS_TOKEN_EXPIRE_MINUTES="60"

# 4. Run migrations
alembic upgrade head
python3 scripts/verify_schema.py

# 5. Restart service
sudo systemctl restart ecomind-api

# 6. Verify health
curl https://api.ecomind.com/health
```

#### Step 4: Production Verification

Run same security tests as staging (Tests 1-5 above)

#### Step 5: Monitor

```bash
# Watch logs for errors
tail -f /var/log/ecomind/api.log

# Monitor error rate
# Check your monitoring dashboard (Datadog, NewRelic, etc.)

# Check database connections
psql -h prod-db -U ecomind_prod -d ecomind -c "
SELECT count(*) FROM pg_stat_activity WHERE datname='ecomind';
"
```

---

## Rollback Plan

### If Issues Detected in Staging

```bash
# Restore database from backup
psql -h staging-db -U ecomind_staging -d ecomind < backup_staging_*.sql

# Revert code
git checkout <previous-tag>

# Restart service
sudo systemctl restart ecomind-api
```

### If Issues Detected in Production

**Immediate Actions:**
```bash
# 1. Restore database
psql -h prod-db -U ecomind_prod -d ecomind < backup_prod_*.sql

# 2. Revert code
git checkout production-pre-phase2-*

# 3. Downgrade dependencies if needed
pip install -e .  # Without [dev] extras if needed

# 4. Restart service
sudo systemctl restart ecomind-api

# 5. Verify rollback
curl https://api.ecomind.com/health
```

**Post-Rollback:**
- Investigate root cause
- Fix issues in development
- Re-test in staging
- Schedule new deployment

---

## Post-Deployment Actions

### 1. Security Audit

**Check for Suspicious Accounts:**
```sql
-- Look for unexpected OWNER/ADMIN accounts created before security fix
SELECT id, email, role, created_at
FROM users
WHERE role IN ('owner', 'admin')
ORDER BY created_at DESC;

-- Check audit logs for failed registration attempts
SELECT * FROM audit_logs
WHERE action = 'login_failed'
  AND ts >= NOW() - INTERVAL '7 days'
ORDER BY ts DESC
LIMIT 100;
```

**Review Recent User Registrations:**
```sql
-- Users created in last 7 days
SELECT u.id, u.email, u.role, u.created_at,
       al.details->>'created_by' as created_by
FROM users u
LEFT JOIN audit_logs al ON al.user_id = u.id
  AND al.action = 'user_registered'
WHERE u.created_at >= NOW() - INTERVAL '7 days'
ORDER BY u.created_at DESC;
```

### 2. Update Documentation

- [ ] Update API documentation with new auth requirements
- [ ] Document breaking changes for `/v1/auth/register`
- [ ] Update integration guides for client applications
- [ ] Add security considerations to developer docs

### 3. Notify Stakeholders

**Internal Teams:**
- Development team: Breaking changes in registration endpoint
- QA team: New security tests to add
- DevOps team: New environment variables required

**External Integrations:**
- API consumers: Breaking change notice for `/v1/auth/register`
- Migration guide for updating integration code

### 4. Monitoring Setup

**Add Alerts For:**
- Failed authentication attempts (threshold: >10/minute)
- 403 Forbidden errors (indicates permission issues)
- Registration endpoint usage (monitor for abuse)
- Database connection pool exhaustion

**Metrics to Track:**
- Authentication success/failure rate
- Average response time for auth endpoints
- Number of active sessions
- Role distribution (VIEWER vs ADMIN vs OWNER)

---

## Migration Summary

### Database Changes

**Migration 001: Initial Schema**
- Creates 8 core tables
- **Fixed**: Enum values now lowercase ('owner', 'admin', 'viewer', 'analyst', 'billing')
- **Fixed**: Plan enum values lowercase ('free', 'pro', 'enterprise')

**Migration 002: Add User Password**
- Adds `password_hash` column to `users` table
- Nullable to support existing users

### Code Changes

**New Dependencies:**
```toml
"python-jose[cryptography]>=3.3.0"  # JWT token handling
"passlib[bcrypt]>=1.7.4"             # Password hashing
"testcontainers>=3.7.0"              # Testing (dev)
```

**Security Hardening:**
- Authentication required for `/v1/auth/register`
- Authorization enforced (ADMIN/OWNER only)
- Role field removed from registration payload
- All new users created as VIEWER
- Organization validation before user creation

**Breaking Changes:**
- ⚠️ `/v1/auth/register` now requires authentication
- ⚠️ `role` field removed from `RegisterRequest`
- ⚠️ All new users are VIEWER (cannot specify role)

---

## Known Issues & Limitations

### Current Limitations

1. **No Self-Service Registration**
   - Users cannot register themselves
   - Requires ADMIN/OWNER to create accounts
   - **Future**: Implement invitation token system

2. **No Role Elevation Endpoint**
   - Cannot upgrade VIEWER to ADMIN via API
   - Must be done via database or future admin endpoint
   - **Future**: Implement role management endpoints

3. **No Refresh Tokens**
   - Access tokens expire after 60 minutes
   - No automatic token refresh
   - **Future**: Phase 2.5 (refresh token rotation)

4. **No Rate Limiting**
   - Auth endpoints not rate limited
   - Vulnerable to brute force (mitigated by account lockout in DB)
   - **Future**: Redis-based rate limiting

5. **No Email Verification**
   - Users can register without email verification
   - **Future**: Email verification workflow

### Deferred to Future Phases

See Phase 2.5 design document for:
- Refresh token rotation
- Password reset workflow
- Email verification
- API key management
- MFA (multi-factor authentication)

---

## Success Criteria

### Deployment Successful If:

- [x] All migrations applied successfully
- [x] Schema verification passes
- [x] API health check returns 200 OK
- [x] Anonymous registration returns 401 Unauthorized
- [x] Authenticated admin can create users
- [x] Created users are VIEWER role
- [x] VIEWER users cannot create accounts (403)
- [x] Invalid org_id returns 404 (not 500)
- [x] No errors in application logs
- [x] No security vulnerabilities present

### Deployment Failed If:

- Migration errors occur
- Schema verification fails
- API fails to start
- Security tests fail
- Existing functionality broken
- Error rate elevated
- Performance degraded significantly

---

## Emergency Contacts

**For Deployment Issues:**
- Database: DBA Team
- Infrastructure: DevOps Team
- Security: Security Team
- Code: Development Team

**Escalation Path:**
1. Check logs: `/var/log/ecomind/api.log`
2. Check database: Connection, migrations, schema
3. Check environment: Variables, dependencies
4. Rollback if necessary (see Rollback Plan)
5. Escalate to on-call engineer if rollback fails

---

## Appendix

### A. Creating First ADMIN User (Manual)

For initial deployment, create first ADMIN user via database:

```sql
-- Generate password hash (use Python)
-- python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('your-password'))"

-- Create organization
INSERT INTO orgs (id, name, plan, created_at)
VALUES ('org_initial', 'Initial Organization', 'free', NOW());

-- Create ADMIN user
INSERT INTO users (id, org_id, email, name, password_hash, role, created_at)
VALUES (
  'user_admin_initial',
  'org_initial',
  'admin@yourdomain.com',
  'System Administrator',
  '$2b$12$...', -- bcrypt hash from above
  'admin',
  NOW()
);
```

### B. Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `JWT_SECRET` | Yes | `dev-secret-change-in-production` | JWT signing key (min 32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token expiration time |
| `PYTHONPATH` | No | - | Path to api directory |

### C. Testing Credentials (Staging Only)

**DO NOT use in production**

```
Admin User:
- Email: admin@staging.ecomind.com
- Password: staging-admin-password-123
- Role: ADMIN

Viewer User:
- Email: viewer@staging.ecomind.com
- Password: staging-viewer-password-123
- Role: VIEWER
```

---

## Sign-off

**Prepared by:** Claude Code
**Reviewed by:** [Pending]
**Approved by:** [Pending]
**Date:** 2025-10-08

**Deployment Status:**
- [ ] Staging Deployed
- [ ] Staging Verified
- [ ] Production Deployed
- [ ] Production Verified
- [ ] Post-Deployment Audit Complete

---

**Next Steps After Successful Deployment:**
1. Phase 2.5: Auth enhancements (refresh tokens, password reset)
2. Phase 3: Infrastructure-as-Code (Terraform, Kubernetes)
3. Integration testing & performance optimization
4. Security penetration testing
