#!/bin/bash
set -euo pipefail

#################################################################
# Dedicated Migration Job Script
#################################################################
#
# PURPOSE:
# Runs database migrations in a separate job/container, NOT on API startup.
#
# PROBLEM ADDRESSED (Codex Review P001):
# Running migrations on every API container start causes:
# - Race conditions across multiple replicas
# - Extended boot times
# - Coupling deployment success to migration health
#
# Reference: phases/P001/codex_review.md:296-303
#
# DEPLOYMENT PATTERN:
# - Kubernetes: Run as init container or Job
# - ECS: Run as separate task before service update
# - Docker Compose: Run as separate service with depends_on
# - Local: Run manually before starting API
#
#################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_RETRIES="${MAX_RETRIES:-5}"
RETRY_DELAY="${RETRY_DELAY:-5}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-60}"

# Parse arguments
COMMAND="${1:-upgrade}"
TARGET="${2:-head}"

show_help() {
    echo "EcoMind Database Migration Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [TARGET]"
    echo ""
    echo "Commands:"
    echo "  upgrade [TARGET]   - Upgrade to TARGET revision (default: head)"
    echo "  downgrade [TARGET] - Downgrade to TARGET revision"
    echo "  current           - Show current database revision"
    echo "  history           - Show migration history"
    echo "  check             - Check if migrations are needed"
    echo "  wait              - Wait for database to be ready (health check)"
    echo ""
    echo "Environment Variables:"
    echo "  DATABASE_URL              - PostgreSQL connection string (REQUIRED)"
    echo "  MAX_RETRIES              - Max connection retries (default: 5)"
    echo "  RETRY_DELAY              - Seconds between retries (default: 5)"
    echo "  HEALTH_CHECK_TIMEOUT     - Max seconds to wait for DB (default: 60)"
    echo ""
    echo "Examples:"
    echo "  $0 upgrade head           # Upgrade to latest"
    echo "  $0 upgrade +1             # Upgrade one revision"
    echo "  $0 downgrade -1           # Downgrade one revision"
    echo "  $0 current                # Show current version"
    echo "  $0 check                  # Check if migrations needed"
    echo ""
    echo "Exit Codes:"
    echo "  0 - Success"
    echo "  1 - Configuration error"
    echo "  2 - Database connection failed"
    echo "  3 - Migration failed"
}

if [ "$COMMAND" = "--help" ] || [ "$COMMAND" = "-h" ]; then
    show_help
    exit 0
fi

# Validate DATABASE_URL
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable not set${NC}"
    echo ""
    echo "Set DATABASE_URL before running migrations:"
    echo ""
    echo "Development:"
    echo "  export DATABASE_URL='postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind'"
    echo ""
    echo "Production (AWS Secrets Manager):"
    echo "  export DATABASE_URL=\$(aws secretsmanager get-secret-value \\"
    echo "    --secret-id ecomind/prod/database \\"
    echo "    --query SecretString --output text | jq -r .connection_string)"
    echo ""
    exit 1
fi

# Extract database details for health check
DB_URL_REGEX="postgresql://([^:]+):([^@]+)@([^:/]+):([0-9]+)/(.+)"
if [[ $DATABASE_URL =~ $DB_URL_REGEX ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASS="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo -e "${RED}ERROR: Invalid DATABASE_URL format${NC}"
    echo "Expected: postgresql://user:password@host:port/dbname"
    exit 1
fi

# Function: Wait for database to be ready
wait_for_database() {
    echo -e "${BLUE}Waiting for database to be ready...${NC}"
    echo "  Host: $DB_HOST:$DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo ""

    local attempt=1
    local start_time=$(date +%s)

    while true; do
        # Check if we've exceeded timeout
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [ $elapsed -ge $HEALTH_CHECK_TIMEOUT ]; then
            echo -e "${RED}ERROR: Database health check timeout after ${HEALTH_CHECK_TIMEOUT}s${NC}"
            exit 2
        fi

        # Try to connect
        if PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
            echo -e "${GREEN}✓ Database is ready (attempt $attempt, ${elapsed}s elapsed)${NC}"
            return 0
        fi

        if [ $attempt -ge $MAX_RETRIES ]; then
            echo -e "${RED}ERROR: Failed to connect after $MAX_RETRIES attempts${NC}"
            exit 2
        fi

        echo -e "${YELLOW}Waiting for database... (attempt $attempt/$MAX_RETRIES)${NC}"
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
}

# Function: Run alembic command
run_alembic() {
    local cmd="$1"
    shift
    local args="$@"

    echo -e "${BLUE}Running: alembic $cmd $args${NC}"

    # Try using python -m alembic (works in containers)
    if python3 -m alembic $cmd $args 2>&1; then
        return 0
    elif alembic $cmd $args 2>&1; then
        return 0
    else
        echo -e "${RED}ERROR: Alembic command failed${NC}"
        return 1
    fi
}

# Main logic
echo -e "${GREEN}=== EcoMind Migration Runner ===${NC}"
echo "Environment: ${ENVIRONMENT:-development}"
echo "Command: $COMMAND $TARGET"
echo ""

# Always wait for database first
wait_for_database

echo ""
echo -e "${BLUE}Current Migration Status:${NC}"
run_alembic current || echo "  (No migrations applied yet)"

echo ""
case "$COMMAND" in
    upgrade)
        echo -e "${GREEN}Upgrading database to: $TARGET${NC}"
        if run_alembic upgrade "$TARGET"; then
            echo -e "${GREEN}✓ Migration successful!${NC}"
            echo ""
            run_alembic current
            exit 0
        else
            echo -e "${RED}✗ Migration failed${NC}"
            exit 3
        fi
        ;;

    downgrade)
        echo -e "${YELLOW}WARNING: Downgrading database to: $TARGET${NC}"
        echo "This may result in data loss!"
        if [ "${SKIP_CONFIRMATION:-false}" != "true" ]; then
            read -p "Continue? (yes/no): " confirm
            if [ "$confirm" != "yes" ]; then
                echo "Aborted by user"
                exit 0
            fi
        fi

        if run_alembic downgrade "$TARGET"; then
            echo -e "${GREEN}✓ Downgrade successful${NC}"
            echo ""
            run_alembic current
            exit 0
        else
            echo -e "${RED}✗ Downgrade failed${NC}"
            exit 3
        fi
        ;;

    current)
        # Already shown above
        exit 0
        ;;

    history)
        run_alembic history --verbose
        exit 0
        ;;

    check)
        echo "Checking if migrations are needed..."
        current=$(run_alembic current 2>&1 | grep -oP '(?<=\(head\)$)' || echo "")
        if [ -z "$current" ]; then
            echo -e "${YELLOW}Migrations needed${NC}"
            exit 1
        else
            echo -e "${GREEN}Database is up to date${NC}"
            exit 0
        fi
        ;;

    wait)
        # Already waited above
        echo -e "${GREEN}Database is ready${NC}"
        exit 0
        ;;

    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
