#!/usr/bin/env python3
"""
Schema Verification Script

This script verifies that the database schema matches expectations.
Useful for:
- Post-migration validation
- Production health checks
- Debugging schema drift issues

SECURITY FIX (Codex Review P001):
- Uses environment-based configuration
- References: phases/P001/codex_review.md:301-302

Usage:
    export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
    python3 scripts/verify_schema.py

    # Or with specific checks:
    python3 scripts/verify_schema.py --tables --indexes --constraints
"""

import os
import sys
from typing import List, Dict, Set
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Inspector


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class SchemaVerifier:
    """Verifies database schema against expected structure."""

    # Expected schema definition
    EXPECTED_TABLES = {
        'orgs': ['id', 'name', 'plan', 'created_at'],
        'users': ['id', 'org_id', 'email', 'name', 'role', 'created_at', 'password_hash'],
        'events_enriched': [
            'id', 'org_id', 'user_id', 'provider', 'model',
            'tokens_in', 'tokens_out', 'node_type', 'region',
            'kwh', 'water_l', 'co2_kg', 'ts', 'source',
            'metadata', 'created_at'
        ],
        'daily_org_agg': ['date', 'org_id', 'call_count', 'kwh', 'water_l', 'co2_kg'],
        'daily_user_agg': ['date', 'org_id', 'user_id', 'call_count', 'kwh', 'water_l', 'co2_kg'],
        'daily_provider_agg': ['date', 'org_id', 'provider', 'call_count', 'kwh', 'water_l', 'co2_kg'],
        'daily_model_agg': ['date', 'org_id', 'provider', 'model', 'call_count', 'kwh', 'water_l', 'co2_kg'],
        'audit_logs': ['id', 'org_id', 'user_id', 'action', 'resource', 'details', 'ts'],
    }

    EXPECTED_INDEXES = {
        'orgs': [],
        'users': ['ix_users_email', 'ix_users_org_id'],  # Unique constraint + FK index
        'events_enriched': [
            'ix_events_org_ts',
            'ix_events_user_ts',
            'ix_events_enriched_org_id',
            'ix_events_enriched_ts',
            'ix_events_enriched_user_id'
        ],
        'daily_org_agg': ['ix_daily_org_date'],
        'daily_user_agg': [],
        'daily_provider_agg': [],
        'daily_model_agg': [],
        'audit_logs': ['ix_audit_logs_org_id', 'ix_audit_logs_ts'],
    }

    EXPECTED_PRIMARY_KEYS = {
        'orgs': ['id'],
        'users': ['id'],
        'events_enriched': ['id'],
        'daily_org_agg': ['date', 'org_id'],
        'daily_user_agg': ['date', 'org_id', 'user_id'],
        'daily_provider_agg': ['date', 'org_id', 'provider'],
        'daily_model_agg': ['date', 'org_id', 'provider', 'model'],
        'audit_logs': ['id'],
    }

    EXPECTED_FOREIGN_KEYS = {
        'users': [('org_id', 'orgs', 'id')],
    }

    def __init__(self, database_url: str):
        """Initialize verifier with database connection."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.inspector: Inspector = inspect(self.engine)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def verify_all(self) -> bool:
        """Run all verification checks."""
        print(f"{Colors.BLUE}=== EcoMind Schema Verification ==={Colors.NC}\n")

        checks = [
            ("Alembic Version Table", self.verify_alembic_version),
            ("Tables", self.verify_tables),
            ("Columns", self.verify_columns),
            ("Primary Keys", self.verify_primary_keys),
            ("Foreign Keys", self.verify_foreign_keys),
            ("Indexes", self.verify_indexes),
        ]

        for name, check_func in checks:
            print(f"{Colors.BLUE}Checking {name}...{Colors.NC}")
            check_func()
            print()

        return self.print_summary()

    def verify_alembic_version(self):
        """Check if alembic_version table exists and has a version."""
        if 'alembic_version' not in self.inspector.get_table_names():
            self.warnings.append("alembic_version table not found - database not managed by Alembic")
            print(f"{Colors.YELLOW}  ⚠ alembic_version table not found{Colors.NC}")
            return

        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
            if result:
                version = result[0]
                print(f"{Colors.GREEN}  ✓ Alembic version: {version}{Colors.NC}")
            else:
                self.errors.append("alembic_version table is empty")
                print(f"{Colors.RED}  ✗ alembic_version table is empty{Colors.NC}")

    def verify_tables(self):
        """Verify all expected tables exist."""
        actual_tables = set(self.inspector.get_table_names())
        expected_tables = set(self.EXPECTED_TABLES.keys())

        missing = expected_tables - actual_tables
        extra = actual_tables - expected_tables - {'alembic_version'}

        if missing:
            for table in sorted(missing):
                self.errors.append(f"Missing table: {table}")
                print(f"{Colors.RED}  ✗ Missing: {table}{Colors.NC}")

        if extra:
            for table in sorted(extra):
                self.warnings.append(f"Extra table: {table}")
                print(f"{Colors.YELLOW}  ⚠ Extra: {table}{Colors.NC}")

        found = expected_tables & actual_tables
        if found and not missing:
            print(f"{Colors.GREEN}  ✓ All {len(expected_tables)} expected tables found{Colors.NC}")

    def verify_columns(self):
        """Verify all expected columns exist in each table."""
        for table_name, expected_columns in self.EXPECTED_TABLES.items():
            try:
                actual_columns = {col['name'] for col in self.inspector.get_columns(table_name)}
                expected = set(expected_columns)

                missing = expected - actual_columns
                extra = actual_columns - expected

                if missing:
                    for col in sorted(missing):
                        self.errors.append(f"Table {table_name}: missing column {col}")
                        print(f"{Colors.RED}  ✗ {table_name}: missing column '{col}'{Colors.NC}")

                if extra:
                    for col in sorted(extra):
                        self.warnings.append(f"Table {table_name}: extra column {col}")
                        print(f"{Colors.YELLOW}  ⚠ {table_name}: extra column '{col}'{Colors.NC}")

                if not missing and not extra:
                    print(f"{Colors.GREEN}  ✓ {table_name}: all {len(expected)} columns present{Colors.NC}")

            except Exception as e:
                self.errors.append(f"Could not check columns for {table_name}: {e}")
                print(f"{Colors.RED}  ✗ {table_name}: error checking columns{Colors.NC}")

    def verify_primary_keys(self):
        """Verify primary key constraints."""
        for table_name, expected_pk_cols in self.EXPECTED_PRIMARY_KEYS.items():
            try:
                pk = self.inspector.get_pk_constraint(table_name)
                actual_pk_cols = pk.get('constrained_columns', [])

                if set(actual_pk_cols) != set(expected_pk_cols):
                    self.errors.append(
                        f"Table {table_name}: PK mismatch. "
                        f"Expected {expected_pk_cols}, got {actual_pk_cols}"
                    )
                    print(f"{Colors.RED}  ✗ {table_name}: PK mismatch{Colors.NC}")
                    print(f"    Expected: {expected_pk_cols}")
                    print(f"    Actual: {actual_pk_cols}")
                else:
                    print(f"{Colors.GREEN}  ✓ {table_name}: PK correct ({', '.join(expected_pk_cols)}){Colors.NC}")

            except Exception as e:
                self.errors.append(f"Could not check PK for {table_name}: {e}")
                print(f"{Colors.RED}  ✗ {table_name}: error checking PK{Colors.NC}")

    def verify_foreign_keys(self):
        """Verify foreign key constraints."""
        for table_name, expected_fks in self.EXPECTED_FOREIGN_KEYS.items():
            try:
                actual_fks = self.inspector.get_foreign_keys(table_name)

                # Convert to comparable format
                actual_fk_set = {
                    (fk['constrained_columns'][0], fk['referred_table'], fk['referred_columns'][0])
                    for fk in actual_fks
                }
                expected_fk_set = set(expected_fks)

                missing = expected_fk_set - actual_fk_set
                extra = actual_fk_set - expected_fk_set

                if missing:
                    for fk in missing:
                        self.errors.append(f"Table {table_name}: missing FK {fk}")
                        print(f"{Colors.RED}  ✗ {table_name}: missing FK {fk[0]} -> {fk[1]}.{fk[2]}{Colors.NC}")

                if extra:
                    for fk in extra:
                        self.warnings.append(f"Table {table_name}: extra FK {fk}")
                        print(f"{Colors.YELLOW}  ⚠ {table_name}: extra FK {fk[0]} -> {fk[1]}.{fk[2]}{Colors.NC}")

                if not missing and not extra and expected_fks:
                    print(f"{Colors.GREEN}  ✓ {table_name}: all {len(expected_fks)} FKs correct{Colors.NC}")

            except Exception as e:
                self.errors.append(f"Could not check FKs for {table_name}: {e}")
                print(f"{Colors.RED}  ✗ {table_name}: error checking FKs{Colors.NC}")

    def verify_indexes(self):
        """Verify expected indexes exist."""
        for table_name, expected_index_names in self.EXPECTED_INDEXES.items():
            try:
                actual_indexes = self.inspector.get_indexes(table_name)
                # Also get primary key indexes and unique constraints
                pk = self.inspector.get_pk_constraint(table_name)
                uniques = self.inspector.get_unique_constraints(table_name)

                # Collect all index names (including PK and unique constraint indexes)
                actual_index_names = {idx['name'] for idx in actual_indexes if idx['name']}
                if pk.get('name'):
                    actual_index_names.add(pk['name'])
                for uq in uniques:
                    if uq.get('name'):
                        actual_index_names.add(uq['name'])

                expected = set(expected_index_names)
                missing = expected - actual_index_names

                if missing:
                    for idx in sorted(missing):
                        self.warnings.append(f"Table {table_name}: missing index {idx}")
                        print(f"{Colors.YELLOW}  ⚠ {table_name}: missing index '{idx}'{Colors.NC}")
                elif expected:
                    print(f"{Colors.GREEN}  ✓ {table_name}: all {len(expected)} indexes present{Colors.NC}")

            except Exception as e:
                self.errors.append(f"Could not check indexes for {table_name}: {e}")
                print(f"{Colors.RED}  ✗ {table_name}: error checking indexes{Colors.NC}")

    def print_summary(self) -> bool:
        """Print verification summary and return success status."""
        print(f"{Colors.BLUE}=== Summary ==={Colors.NC}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print()

        if self.errors:
            print(f"{Colors.RED}FAILED: Schema verification found {len(self.errors)} errors{Colors.NC}")
            for error in self.errors:
                print(f"  - {error}")
            return False

        if self.warnings:
            print(f"{Colors.YELLOW}PASSED WITH WARNINGS: {len(self.warnings)} warnings{Colors.NC}")
            for warning in self.warnings:
                print(f"  - {warning}")
            return True

        print(f"{Colors.GREEN}PASSED: Schema verification successful{Colors.NC}")
        return True


def main():
    """Main entry point."""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print(f"{Colors.RED}ERROR: DATABASE_URL environment variable not set{Colors.NC}")
        print()
        print("Set DATABASE_URL before running schema verification:")
        print("  export DATABASE_URL='postgresql://user:password@host:5432/ecomind'")
        print()
        sys.exit(1)

    # Mask password in output
    display_url = database_url.split('@')[1] if '@' in database_url else database_url
    print(f"Database: {display_url}")
    print()

    try:
        verifier = SchemaVerifier(database_url)
        success = verifier.verify_all()
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"{Colors.RED}FATAL ERROR: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
