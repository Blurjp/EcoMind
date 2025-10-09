# Deployment Checklist - Quick Reference

**Date:** 2025-10-08
**Version:** Phase 1 + Phase 2

---

## Pre-Deployment

### Environment Setup
- [ ] `DATABASE_URL` environment variable set
- [ ] `JWT_SECRET` environment variable set (min 32 chars, use `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` set (default: 60)
- [ ] Python dependencies installed: `pip install -e ".[dev]"`

### Database Preparation
- [ ] Database backup created
- [ ] Migrations ready: `alembic upgrade head`
- [ ] Schema verification passed: `python3 scripts/verify_schema.py`

### Code Verification
- [ ] Latest code pulled from `main` branch
- [ ] Security fixes included (check git log)
- [ ] Dependencies updated in `pyproject.toml`

---

## Staging Deployment

### Deploy Steps
1. [ ] Backup staging database
2. [ ] Pull latest code: `git pull origin main`
3. [ ] Install dependencies: `pip install -e ".[dev]"`
4. [ ] Set environment variables
5. [ ] Run migrations: `alembic upgrade head`
6. [ ] Verify schema: `python3 scripts/verify_schema.py`
7. [ ] Restart API service
8. [ ] Health check: `curl http://staging/health`

### Security Verification
- [ ] Test 1: Anonymous registration blocked (401)
- [ ] Test 2: Login works (200 + token)
- [ ] Test 3: ADMIN can create users (201)
- [ ] Test 4: VIEWER cannot create users (403)
- [ ] Test 5: Invalid org_id returns 404 (not 500)

### Post-Staging
- [ ] No errors in logs (24 hours)
- [ ] Performance acceptable
- [ ] All stakeholders notified

---

## Production Deployment

### Pre-Production
- [ ] Staging verified ✅
- [ ] Backup created
- [ ] Maintenance window scheduled (if needed)
- [ ] Rollback plan reviewed

### Deploy Steps
1. [ ] Backup production database
2. [ ] Tag current state: `git tag production-pre-phase2-$(date +%Y%m%d)`
3. [ ] Pull latest code
4. [ ] Install dependencies
5. [ ] Set production environment variables (different JWT_SECRET!)
6. [ ] Run migrations: `alembic upgrade head`
7. [ ] Verify schema
8. [ ] Restart API service
9. [ ] Health check
10. [ ] Run security tests (same as staging)

### Post-Production
- [ ] Monitor logs (first 24 hours)
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Stakeholders notified

---

## Security Audit

### Database Checks
```sql
-- Check for suspicious OWNER/ADMIN accounts
SELECT id, email, role, created_at FROM users
WHERE role IN ('owner', 'admin')
ORDER BY created_at DESC;

-- Check recent registrations
SELECT * FROM audit_logs
WHERE action = 'user_registered'
  AND ts >= NOW() - INTERVAL '7 days'
ORDER BY ts DESC;
```

### Results
- [ ] No suspicious accounts found
- [ ] All recent registrations legitimate
- [ ] Audit logs reviewed

---

## Rollback Plan

### If Issues in Staging
```bash
psql -h staging-db -d ecomind < backup_staging_*.sql
git checkout <previous-tag>
sudo systemctl restart ecomind-api
```

### If Issues in Production
```bash
psql -h prod-db -d ecomind < backup_prod_*.sql
git checkout production-pre-phase2-*
sudo systemctl restart ecomind-api
curl https://api.ecomind.com/health  # Verify
```

---

## Emergency Commands

### Quick Health Check
```bash
curl http://api/health
curl http://api/
```

### Check Migration Status
```bash
alembic current
alembic history
```

### View Logs
```bash
tail -f /var/log/ecomind/api.log
```

### Database Connection
```bash
psql -h <host> -U <user> -d ecomind
```

---

## Success Criteria

**Deployment Successful:**
- ✅ All migrations applied
- ✅ Schema verification passes
- ✅ API health check OK
- ✅ Security tests pass
- ✅ No errors in logs

**Deployment Failed:**
- ❌ Migration errors
- ❌ Security tests fail
- ❌ API won't start
- ❌ High error rate

**Action if Failed:** Execute rollback immediately

---

## Contact Information

- **Database Issues:** DBA Team
- **Infrastructure:** DevOps Team
- **Security:** Security Team
- **Application:** Development Team

---

## Sign-off

- [ ] Staging Deployed & Verified
- [ ] Production Deployed & Verified
- [ ] Post-Deployment Audit Complete
- [ ] Documentation Updated
- [ ] Stakeholders Notified

**Deployment Manager:** ___________________
**Date:** ___________________
**Status:** ___________________
