#!/bin/bash
# Deployment Verification Script
# Verifies EcoMind API deployment is successful

set -e

echo "🔍 EcoMind API Deployment Verification"
echo "========================================"
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TEST_EMAIL="${TEST_EMAIL:-admin@test.com}"

# Test counters
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# Test 1: Health Check
echo "Test 1: Health Check"
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    pass "Health endpoint responding"
else
    fail "Health endpoint not responding"
fi
echo

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
RESPONSE=$(curl -s "$API_URL/" 2>/dev/null || echo "")
if echo "$RESPONSE" | grep -q "ecomind-api"; then
    pass "Root endpoint responding with service name"
else
    fail "Root endpoint not responding correctly"
fi
echo

# Test 3: Anonymous Registration Blocked
echo "Test 3: Anonymous Registration Blocked (Security)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$API_URL/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"attacker@evil.com","password":"test","name":"Attacker","org_id":"org_test"}' \
    2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "401" ]; then
    pass "Anonymous registration correctly blocked (401)"
elif [ "$HTTP_CODE" = "422" ]; then
    pass "Anonymous registration blocked (422 - validation error)"
else
    fail "Anonymous registration not properly blocked (got HTTP $HTTP_CODE, expected 401)"
fi
echo

# Test 4: Database Connection
echo "Test 4: Database Connection"
if [ -n "$DATABASE_URL" ]; then
    # Try to connect using psql
    if command -v psql > /dev/null 2>&1; then
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        if [ -n "$DB_HOST" ]; then
            if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
                pass "Database connection successful"
            else
                fail "Database connection failed"
            fi
        else
            warn "Could not parse database host from DATABASE_URL"
        fi
    else
        warn "psql not installed, skipping database connection test"
    fi
else
    warn "DATABASE_URL not set, skipping database connection test"
fi
echo

# Test 5: Environment Variables
echo "Test 5: Environment Variables"
if [ -n "$DATABASE_URL" ]; then
    pass "DATABASE_URL is set"
else
    fail "DATABASE_URL is not set"
fi

if [ -n "$JWT_SECRET" ]; then
    if [ ${#JWT_SECRET} -ge 32 ]; then
        pass "JWT_SECRET is set and sufficiently long (${#JWT_SECRET} chars)"
    else
        warn "JWT_SECRET is set but short (${#JWT_SECRET} chars, recommend 32+)"
    fi
else
    warn "JWT_SECRET is not set (will use dev default)"
fi
echo

# Test 6: Migration Status
echo "Test 6: Migration Status"
if command -v alembic > /dev/null 2>&1; then
    CURRENT=$(alembic current 2>/dev/null | grep -v "INFO" || echo "")
    if echo "$CURRENT" | grep -q "002"; then
        pass "Migrations applied (at revision 002)"
    elif echo "$CURRENT" | grep -q "001"; then
        warn "Only migration 001 applied (002 pending)"
    else
        fail "No migrations applied or alembic not configured"
    fi
else
    warn "alembic not installed, skipping migration check"
fi
echo

# Test 7: Dependencies
echo "Test 7: Python Dependencies"
python3 -c "import fastapi" 2>/dev/null && pass "fastapi installed" || fail "fastapi not installed"
python3 -c "import sqlalchemy" 2>/dev/null && pass "sqlalchemy installed" || fail "sqlalchemy not installed"
python3 -c "import alembic" 2>/dev/null && pass "alembic installed" || fail "alembic not installed"
python3 -c "import jose" 2>/dev/null && pass "python-jose installed" || fail "python-jose not installed"
python3 -c "import passlib" 2>/dev/null && pass "passlib installed" || fail "passlib not installed"
echo

# Summary
echo "========================================"
echo "Summary:"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment verification PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ Deployment verification FAILED${NC}"
    echo "Please review failed tests above"
    exit 1
fi
