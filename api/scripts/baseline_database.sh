#!/bin/bash
set -euo pipefail

#################################################################
# Database Baselining Script for Existing EcoMind Databases
#################################################################
#
# PURPOSE:
# This script "baselines" an existing database by stamping it with
# the initial migration revision WITHOUT running the migration itself.
#
# PROBLEM ADDRESSED (Codex Review P001):
# Running the initial migration (001_initial_schema.py) on an existing
# database will fail because tables already exist. This script marks
# the database as being at revision '001' without creating tables.
#
# Reference: phases/P001/codex_review.md:293-300
#
# WHEN TO USE:
# - Migrating from manually-managed schema to Alembic
# - Existing production/staging databases with tables already created
# - Development databases that were created before migrations existed
#
# WHEN NOT TO USE:
# - Brand new databases (just run 'alembic upgrade head')
# - Databases already managed by Alembic
#
# SAFETY CHECKS:
# 1. Verifies all expected tables exist before stamping
# 2. Checks that alembic_version table doesn't already exist
# 3. Creates dry-run report before making changes
# 4. Supports rollback via --undo flag
#
#################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EXPECTED_TABLES=(
    "orgs"
    "users"
    "events_enriched"
    "daily_org_agg"
    "daily_user_agg"
    "daily_provider_agg"
    "daily_model_agg"
    "audit_logs"
)
INITIAL_REVISION="001"

# Parse arguments
DRY_RUN=false
UNDO=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --undo)
            UNDO=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be done without making changes"
            echo "  --undo       Remove baseline stamp (use with caution!)"
            echo "  --verbose    Show detailed output"
            echo "  --help       Show this help message"
            echo ""
            echo "Environment Variables Required:"
            echo "  DATABASE_URL - PostgreSQL connection string"
            echo ""
            echo "Example:"
            echo "  export DATABASE_URL='postgresql://user:pass@host:5432/ecomind'"
            echo "  $0 --dry-run"
            echo "  $0"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Check DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable not set${NC}"
    echo ""
    echo "Please set DATABASE_URL before running this script:"
    echo "  export DATABASE_URL='postgresql://user:password@host:5432/ecomind'"
    echo ""
    echo "For production, retrieve from AWS Secrets Manager:"
    echo "  export DATABASE_URL=\$(aws secretsmanager get-secret-value \\
    echo "    --secret-id ecomind/prod/database --query SecretString --output text)"
    exit 1
fi

# Extract connection details from DATABASE_URL for psql
# Format: postgresql://user:password@host:port/dbname
DB_URL_REGEX="postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+)"
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

# Function to run SQL query
run_query() {
    local query="$1"
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$query" 2>/dev/null
}

echo -e "${GREEN}=== EcoMind Database Baselining Tool ===${NC}"
echo ""
echo "Target Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "Mode: $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "LIVE")"
echo ""

# Step 1: Check if alembic_version table already exists
echo "Step 1: Checking for existing Alembic version table..."
alembic_exists=$(run_query "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');" | tr -d '[:space:]')

if [ "$UNDO" = true ]; then
    if [ "$alembic_exists" = "f" ]; then
        echo -e "${YELLOW}WARNING: alembic_version table doesn't exist. Nothing to undo.${NC}"
        exit 0
    fi

    current_version=$(run_query "SELECT version_num FROM alembic_version;" | tr -d '[:space:]')
    echo -e "${YELLOW}Current revision: $current_version${NC}"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] Would remove alembic_version table${NC}"
    else
        echo -e "${RED}Removing alembic_version table...${NC}"
        run_query "DROP TABLE alembic_version;"
        echo -e "${GREEN}✓ Baseline removed${NC}"
    fi
    exit 0
fi

if [ "$alembic_exists" = "t" ]; then
    current_version=$(run_query "SELECT version_num FROM alembic_version;" | tr -d '[:space:]')
    echo -e "${RED}ERROR: Database is already managed by Alembic (revision: $current_version)${NC}"
    echo ""
    echo "This script should only be used on databases not yet under Alembic management."
    echo "If you want to remove the current baseline, run: $0 --undo"
    exit 1
fi
echo -e "${GREEN}✓ No existing Alembic version table${NC}"

# Step 2: Verify all expected tables exist
echo ""
echo "Step 2: Verifying all expected tables exist..."
missing_tables=()
for table in "${EXPECTED_TABLES[@]}"; do
    exists=$(run_query "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$table');" | tr -d '[:space:]')
    if [ "$exists" = "f" ]; then
        missing_tables+=("$table")
        echo -e "${RED}  ✗ Missing: $table${NC}"
    else
        echo -e "${GREEN}  ✓ Found: $table${NC}"
    fi
done

if [ ${#missing_tables[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Missing ${#missing_tables[@]} required tables${NC}"
    echo ""
    echo "The following tables are missing:"
    for table in "${missing_tables[@]}"; do
        echo "  - $table"
    done
    echo ""
    echo "OPTIONS:"
    echo "1. Create missing tables manually using SQL from migration file"
    echo "2. Run 'alembic upgrade head' on empty database instead of baselining"
    echo "3. Fix table names if they don't match expected names"
    exit 1
fi

# Step 3: Show table row counts (for verification)
echo ""
echo "Step 3: Current table row counts (for verification)..."
for table in "${EXPECTED_TABLES[@]}"; do
    count=$(run_query "SELECT COUNT(*) FROM $table;" | tr -d '[:space:]')
    echo "  $table: $count rows"
done

# Step 4: Baseline the database
echo ""
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would execute:${NC}"
    echo "  CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);"
    echo "  INSERT INTO alembic_version (version_num) VALUES ('$INITIAL_REVISION');"
    echo ""
    echo "This would mark the database as being at revision '$INITIAL_REVISION'."
    echo ""
    echo "To apply for real, run without --dry-run flag."
else
    echo "Step 4: Applying baseline (stamping revision $INITIAL_REVISION)..."
    read -p "This will modify the database. Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted by user."
        exit 0
    fi

    run_query "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);"
    run_query "INSERT INTO alembic_version (version_num) VALUES ('$INITIAL_REVISION');"

    echo -e "${GREEN}✓ Database baselined successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Verify: alembic current"
    echo "2. Test upgrade: alembic upgrade head (should show 'Running upgrade 001 -> 002' if new migrations exist)"
    echo "3. For production: Document this baseline in deployment log"
fi

echo ""
echo -e "${GREEN}=== Baseline Complete ===${NC}"
