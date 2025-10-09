#!/bin/bash
# Local Deployment Script for EcoMind API
# This script demonstrates the full deployment process

set -e

echo "🚀 EcoMind API - Local Deployment"
echo "=================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the api directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must run from api directory${NC}"
    exit 1
fi

# Step 1: Activate virtual environment
echo "Step 1: Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo

# Step 2: Install dependencies
echo "Step 2: Installing dependencies..."
pip install -e ".[dev]" --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo

# Step 3: Load environment variables
echo "Step 3: Loading environment variables..."
if [ -f ".env.local" ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Environment variables loaded from .env.local${NC}"
else
    echo -e "${YELLOW}⚠️  No .env.local file found${NC}"
    echo "Creating default environment file..."
    cat > .env.local << 'EOF'
DATABASE_URL=postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ACCESS_TOKEN_EXPIRE_MINUTES=60
PYTHONPATH=$(pwd)
EOF
    export $(cat .env.local | grep -v '^#' | xargs)
fi
echo

# Step 4: Check database availability
echo "Step 4: Checking database..."
if command -v psql >/dev/null 2>&1; then
    if psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection successful${NC}"

        # Run migrations
        echo
        echo "Step 5: Running database migrations..."
        alembic current
        alembic upgrade head
        echo -e "${GREEN}✅ Migrations applied${NC}"

        # Verify schema
        echo
        echo "Step 6: Verifying schema..."
        python3 scripts/verify_schema.py
    else
        echo -e "${YELLOW}⚠️  Database not accessible${NC}"
        echo
        echo "To start a PostgreSQL database with Docker:"
        echo "  docker run --name ecomind-postgres \\"
        echo "    -e POSTGRES_USER=ecomind \\"
        echo "    -e POSTGRES_PASSWORD=ecomind_dev_pass \\"
        echo "    -e POSTGRES_DB=ecomind \\"
        echo "    -p 5432:5432 -d postgres:15"
        echo
        echo "Then run migrations:"
        echo "  alembic upgrade head"
        echo
    fi
else
    echo -e "${YELLOW}⚠️  PostgreSQL client (psql) not found${NC}"
    echo "Install with: brew install postgresql (macOS)"
    echo
fi

# Step 7: Start API
echo
echo "Step 7: Starting API server..."
echo -e "${GREEN}Ready to start API!${NC}"
echo
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  export \$(cat .env.local | grep -v '^#' | xargs)"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "Or run in background:"
echo "  nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &"
echo
echo "Then verify deployment:"
echo "  bash scripts/deploy_verify.sh"
echo
echo "=================================="
echo -e "${GREEN}Deployment preparation complete!${NC}"
