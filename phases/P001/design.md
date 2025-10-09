# Phase 1: Database Migration Infrastructure

**Phase ID**: P001
**Duration**: 1 week (5 business days)
**Priority**: HIGH (BLOCKING for production)
**Owner**: Backend Team
**Status**: Design Review

---

## 1. Executive Summary

Implement Alembic-based database migration infrastructure to enable versioned schema changes, rollback capability, and safe schema evolution across development, staging, and production environments.

**Problem Statement:**
- Current schema is manually managed via raw SQL in worker enrichment service
- No version control for schema changes
- No rollback mechanism for failed deployments
- Schema drift risk between environments
- Team collaboration issues (conflicting schema changes)

**Success Criteria:**
- ✅ Alembic migrations working in all environments (dev/staging/prod)
- ✅ All existing tables captured in initial migration
- ✅ Migration rollback tested successfully
- ✅ CI/CD pipeline runs migrations automatically
- ✅ Developer documentation complete

---

## 2. Technical Architecture

### 2.1 Current State Analysis

**Evidence from codebase:**

**File**: `worker/worker/services/enrichment.py:78-159`
```python
# Current approach: Raw SQL with ON CONFLICT
db.execute(
    text("""
        INSERT INTO events_enriched
        (id, org_id, user_id, provider, model, tokens_in, tokens_out,
         node_type, region, kwh, water_l, co2_kg, ts, source, metadata, created_at)
        VALUES
        (gen_random_uuid()::text, :org_id, :user_id, :provider, :model, :tokens_in, :tokens_out,
         :node_type, :region, :kwh, :water_l, :co2_kg, :ts, :source, :metadata::jsonb, now())
    """),
    {...}
)
```

**Issues:**
1. No CREATE TABLE statements in version control
2. Schema changes require manual SQL execution
3. No audit trail of schema evolution
4. Rollback requires manual DROP/ALTER statements

**File**: `api/app/db.py:1-22`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Missing:** No migration directory, no Alembic config.

### 2.2 Proposed Architecture

```
EcoMind/
├── api/
│   ├── alembic/                      # NEW: Migration directory
│   │   ├── versions/                 # Migration scripts
│   │   │   ├── 001_initial_schema.py
│   │   │   ├── 002_add_indexes.py
│   │   │   └── ...
│   │   ├── env.py                    # Alembic environment
│   │   └── script.py.mako            # Template for new migrations
│   ├── alembic.ini                   # Alembic config
│   ├── app/
│   │   ├── models/                   # SQLAlchemy models (authoritative)
│   │   │   ├── org.py
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── aggregate.py
│   │   │   └── audit.py
│   │   └── db.py                     # Database connection
│   └── scripts/
│       ├── migrate.sh                # NEW: Migration wrapper script
│       └── verify_schema.py          # NEW: Schema validation
└── docker-compose.dev.yml            # Updated with migration step
```

### 2.3 Database Schema (Captured in Initial Migration)

**Tables to capture:**

1. **organizations**
   ```sql
   CREATE TABLE organizations (
       org_id VARCHAR(255) PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       plan_type VARCHAR(50) DEFAULT 'free',
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

2. **users**
   ```sql
   CREATE TABLE users (
       user_id VARCHAR(255) PRIMARY KEY,
       org_id VARCHAR(255) REFERENCES organizations(org_id) ON DELETE CASCADE,
       email VARCHAR(255) UNIQUE,
       role VARCHAR(50) DEFAULT 'viewer',
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_users_org_id ON users(org_id);
   CREATE INDEX idx_users_email ON users(email);
   ```

3. **events_enriched**
   ```sql
   CREATE TABLE events_enriched (
       id TEXT PRIMARY KEY,
       org_id VARCHAR(255) NOT NULL,
       user_id VARCHAR(255) NOT NULL,
       provider VARCHAR(50) NOT NULL,
       model VARCHAR(100),
       tokens_in INTEGER DEFAULT 0,
       tokens_out INTEGER DEFAULT 0,
       node_type VARCHAR(50),
       region VARCHAR(100),
       kwh FLOAT NOT NULL,
       water_l FLOAT NOT NULL,
       co2_kg FLOAT NOT NULL,
       ts TIMESTAMPTZ NOT NULL,
       source VARCHAR(50),
       metadata JSONB,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_events_org_id ON events_enriched(org_id);
   CREATE INDEX idx_events_ts ON events_enriched(ts);
   CREATE INDEX idx_events_provider ON events_enriched(provider);
   ```

4. **daily_org_agg**
   ```sql
   CREATE TABLE daily_org_agg (
       date DATE NOT NULL,
       org_id VARCHAR(255) NOT NULL,
       call_count INTEGER DEFAULT 0,
       kwh FLOAT DEFAULT 0.0,
       water_l FLOAT DEFAULT 0.0,
       co2_kg FLOAT DEFAULT 0.0,
       PRIMARY KEY (date, org_id)
   );
   CREATE INDEX idx_daily_org_agg_date ON daily_org_agg(date);
   ```

5. **daily_user_agg**
   ```sql
   CREATE TABLE daily_user_agg (
       date DATE NOT NULL,
       org_id VARCHAR(255) NOT NULL,
       user_id VARCHAR(255) NOT NULL,
       call_count INTEGER DEFAULT 0,
       kwh FLOAT DEFAULT 0.0,
       water_l FLOAT DEFAULT 0.0,
       co2_kg FLOAT DEFAULT 0.0,
       PRIMARY KEY (date, org_id, user_id)
   );
   CREATE INDEX idx_daily_user_agg_date ON daily_user_agg(date);
   CREATE INDEX idx_daily_user_agg_org_id ON daily_user_agg(org_id);
   ```

6. **daily_provider_agg**
   ```sql
   CREATE TABLE daily_provider_agg (
       date DATE NOT NULL,
       org_id VARCHAR(255) NOT NULL,
       provider VARCHAR(50) NOT NULL,
       call_count INTEGER DEFAULT 0,
       kwh FLOAT DEFAULT 0.0,
       water_l FLOAT DEFAULT 0.0,
       co2_kg FLOAT DEFAULT 0.0,
       PRIMARY KEY (date, org_id, provider)
   );
   CREATE INDEX idx_daily_provider_agg_date ON daily_provider_agg(date);
   ```

7. **daily_model_agg**
   ```sql
   CREATE TABLE daily_model_agg (
       date DATE NOT NULL,
       org_id VARCHAR(255) NOT NULL,
       provider VARCHAR(50) NOT NULL,
       model VARCHAR(100) NOT NULL,
       call_count INTEGER DEFAULT 0,
       kwh FLOAT DEFAULT 0.0,
       water_l FLOAT DEFAULT 0.0,
       co2_kg FLOAT DEFAULT 0.0,
       PRIMARY KEY (date, org_id, provider, model)
   );
   CREATE INDEX idx_daily_model_agg_date ON daily_model_agg(date);
   ```

8. **audit_logs**
   ```sql
   CREATE TABLE audit_logs (
       id BIGSERIAL PRIMARY KEY,
       org_id VARCHAR(255),
       user_id VARCHAR(255),
       action VARCHAR(100) NOT NULL,
       resource_type VARCHAR(100),
       resource_id VARCHAR(255),
       metadata JSONB,
       ip_address VARCHAR(50),
       timestamp TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
   CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
   ```

### 2.4 Alembic Configuration

**alembic.ini**:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**alembic/env.py**:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db import Base
from app.models import *  # Import all models

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment
if os.getenv('DATABASE_URL'):
    config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 3. Implementation Plan

### 3.1 Day 1: Setup & Initial Migration

**Tasks:**
1. Install Alembic in API service
   ```bash
   cd api
   pip install alembic
   ```

2. Initialize Alembic
   ```bash
   alembic init alembic
   ```

3. Update `alembic.ini` with database URL pattern

4. Create SQLAlchemy models for all tables (if not already complete)

5. Generate initial migration
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   ```

6. Review and adjust generated migration

**Deliverables:**
- ✅ `alembic/` directory structure
- ✅ `alembic.ini` configuration
- ✅ Initial migration in `alembic/versions/001_initial_schema.py`

### 3.2 Day 2: Index Optimization Migration

**Tasks:**
1. Analyze query patterns in `api/app/routes/query.py`

2. Create second migration for performance indexes
   ```bash
   alembic revision -m "Add performance indexes"
   ```

3. Add indexes for:
   - `events_enriched(org_id, ts)` - composite for time-range queries
   - `daily_user_agg(org_id, date)` - composite for user aggregates
   - `audit_logs(org_id, timestamp)` - composite for audit queries

**Deliverables:**
- ✅ `002_add_performance_indexes.py` migration

### 3.3 Day 3: Migration Scripts & Testing

**Tasks:**
1. Create `scripts/migrate.sh` wrapper
   ```bash
   #!/bin/bash
   set -e

   echo "🔄 Running database migrations..."

   # Wait for database to be ready
   until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\q'; do
     echo "⏳ Waiting for database..."
     sleep 2
   done

   # Run migrations
   alembic upgrade head

   echo "✅ Migrations complete"
   ```

2. Create `scripts/verify_schema.py` validation script
   ```python
   import psycopg2
   import os

   def verify_schema():
       conn = psycopg2.connect(os.getenv('DATABASE_URL'))
       cursor = conn.cursor()

       # Check all tables exist
       tables = ['organizations', 'users', 'events_enriched', 'daily_org_agg',
                 'daily_user_agg', 'daily_provider_agg', 'daily_model_agg', 'audit_logs']

       cursor.execute("""
           SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'
       """)
       existing_tables = [row[0] for row in cursor.fetchall()]

       for table in tables:
           assert table in existing_tables, f"Missing table: {table}"

       print("✅ All tables exist")

       # Check alembic_version table
       cursor.execute("SELECT version_num FROM alembic_version")
       version = cursor.fetchone()[0]
       print(f"✅ Migration version: {version}")

       conn.close()

   if __name__ == '__main__':
       verify_schema()
   ```

3. Test migration flow:
   ```bash
   # Fresh database
   docker-compose down -v
   docker-compose up -d postgres

   # Run migrations
   cd api
   alembic upgrade head

   # Verify
   python scripts/verify_schema.py

   # Test rollback
   alembic downgrade -1
   alembic upgrade head
   ```

**Deliverables:**
- ✅ Migration scripts working
- ✅ Rollback tested successfully

### 3.4 Day 4: CI/CD Integration

**Tasks:**
1. Update `docker-compose.dev.yml` to run migrations on startup
   ```yaml
   api:
     build: ./api
     command: >
       sh -c "alembic upgrade head &&
              uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
     depends_on:
       postgres:
         condition: service_healthy
   ```

2. Create GitHub Actions workflow `.github/workflows/migrate.yml`
   ```yaml
   name: Database Migrations

   on:
     push:
       branches: [main, staging]

   jobs:
     migrate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'

         - name: Install dependencies
           run: |
             cd api
             pip install -r requirements.txt

         - name: Run migrations (dry-run)
           run: |
             cd api
             alembic upgrade head --sql > migration.sql
             cat migration.sql

         - name: Upload migration SQL
           uses: actions/upload-artifact@v3
           with:
             name: migration-sql
             path: api/migration.sql
   ```

3. Document deployment process in `docs/DEPLOYMENT.md`

**Deliverables:**
- ✅ Docker Compose auto-migration
- ✅ CI/CD pipeline for migrations

### 3.5 Day 5: Documentation & Handoff

**Tasks:**
1. Create `docs/DATABASE_MIGRATIONS.md`
   - How to create new migrations
   - How to test migrations locally
   - How to rollback in production
   - Common issues and troubleshooting

2. Update `CONTRIBUTING.md` with migration workflow

3. Create runbook for production deployment

4. Team training session (1 hour)

**Deliverables:**
- ✅ Complete documentation
- ✅ Team trained

---

## 4. Risk Analysis

### 4.1 High Risks

**Risk 1: Data Loss During Migration**
- **Likelihood**: Low
- **Impact**: Critical
- **Mitigation**:
  - Backup database before migration
  - Test on staging first
  - Use transactions for all migrations
  - Keep rollback scripts ready

**Risk 2: Downtime During Migration**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Use blue-green deployment
  - Run migrations during maintenance window
  - Schema changes should be backward-compatible

### 4.2 Medium Risks

**Risk 3: Migration Conflicts in Team**
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**:
  - Review migrations in PRs
  - Use sequential numbering
  - Resolve conflicts before merge

**Risk 4: Performance Impact**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Create indexes CONCURRENTLY
  - Avoid locking tables during business hours
  - Monitor query performance after migration

---

## 5. Success Metrics

**Quantitative:**
- ✅ 0 manual schema changes after implementation
- ✅ < 5 seconds migration time for typical changes
- ✅ 100% rollback success rate in testing
- ✅ 0 data loss incidents

**Qualitative:**
- ✅ Developer confidence in making schema changes
- ✅ No schema drift between environments
- ✅ Faster deployment cycles

---

## 6. Dependencies

**Upstream (Blockers):**
- None (can start immediately)

**Downstream (Dependent on this):**
- P002: Authentication Enforcement (needs audit_logs table)
- P003: Infrastructure-as-Code (needs migration automation)
- P004: Monitoring (needs schema stability)

---

## 7. Open Questions

1. **TimescaleDB Extension**: Should we enable TimescaleDB hypertables in initial migration or separate migration?
   - **Recommendation**: Separate migration after P001 complete

2. **Migration Testing Strategy**: Unit tests for migrations or just integration tests?
   - **Recommendation**: Integration tests with Docker Compose

3. **Production Migration Approval**: Who approves production migrations?
   - **Recommendation**: Requires both backend lead + DevOps approval

---

## 8. References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [PostgreSQL Migration Guide](https://www.postgresql.org/docs/current/sql-altertable.html)
- Internal: `worker/worker/services/enrichment.py` (current schema usage)
- Internal: `api/app/models/` (SQLAlchemy models)

---

## 9. Acceptance Criteria

- [ ] Alembic installed and configured
- [ ] Initial migration captures all 8 tables
- [ ] Performance indexes migration created
- [ ] Migration scripts (`migrate.sh`, `verify_schema.py`) working
- [ ] Docker Compose runs migrations on startup
- [ ] CI/CD pipeline validates migrations
- [ ] Documentation complete (`DATABASE_MIGRATIONS.md`)
- [ ] Team trained on migration workflow
- [ ] Rollback tested successfully (upgrade → downgrade → upgrade)
- [ ] No data loss in staging environment test

---

**Design Status**: Ready for Codex Review
**Next Step**: Codex review → Implementation → Testing → Production deployment
