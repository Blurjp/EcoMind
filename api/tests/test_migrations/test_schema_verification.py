"""
Tests for schema verification script (scripts/verify_schema.py)

Verifies that the schema verification tool correctly identifies
missing tables, columns, indexes, and constraints.
"""

import pytest
import sys
import os
from pathlib import Path

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from verify_schema import SchemaVerifier
from sqlalchemy import text
from alembic import command
from alembic.config import Config


class TestSchemaVerification:
    """Test suite for schema verification tool."""

    @pytest.fixture
    def alembic_config(self, set_test_env):
        """Create Alembic configuration."""
        config = Config("alembic.ini")
        config.set_main_option("script_location", "alembic")
        config.set_main_option("sqlalchemy.url", set_test_env)
        return config

    @pytest.fixture
    def migrated_database(self, clean_database, alembic_config):
        """Provide a fully migrated database."""
        command.upgrade(alembic_config, "head")
        return clean_database

    def test_verifier_passes_on_correct_schema(self, migrated_database):
        """Test that verifier passes on correctly migrated database."""
        verifier = SchemaVerifier(migrated_database)

        # Run verification
        verifier.verify_tables()
        verifier.verify_columns()
        verifier.verify_primary_keys()
        verifier.verify_foreign_keys()

        # Should have no errors
        assert len(verifier.errors) == 0, f"Unexpected errors: {verifier.errors}"

    def test_verifier_detects_missing_table(self, migrated_database, db_engine):
        """Test that verifier detects missing tables."""
        # Drop a table
        with db_engine.connect() as conn:
            conn.execute(text("DROP TABLE audit_logs CASCADE"))
            conn.commit()

        verifier = SchemaVerifier(migrated_database)
        verifier.verify_tables()

        # Should have error about missing table
        assert len(verifier.errors) > 0
        assert any('audit_logs' in err.lower() for err in verifier.errors)

    def test_verifier_detects_missing_column(self, migrated_database, db_engine):
        """Test that verifier detects missing columns."""
        # Remove a column
        with db_engine.connect() as conn:
            conn.execute(text("ALTER TABLE orgs DROP COLUMN name"))
            conn.commit()

        verifier = SchemaVerifier(migrated_database)
        verifier.verify_columns()

        # Should have error about missing column
        assert len(verifier.errors) > 0
        assert any('name' in err.lower() and 'orgs' in err.lower() for err in verifier.errors)

    def test_verifier_detects_extra_column(self, migrated_database, db_engine):
        """Test that verifier detects extra columns as warnings."""
        # Add an extra column
        with db_engine.connect() as conn:
            conn.execute(text("ALTER TABLE orgs ADD COLUMN extra_field TEXT"))
            conn.commit()

        verifier = SchemaVerifier(migrated_database)
        verifier.verify_columns()

        # Should have warning about extra column
        assert len(verifier.warnings) > 0
        assert any('extra_field' in warn.lower() for warn in verifier.warnings)

    def test_verifier_detects_missing_index(self, migrated_database, db_engine):
        """Test that verifier detects missing indexes."""
        # Drop an index
        with db_engine.connect() as conn:
            conn.execute(text("DROP INDEX IF EXISTS ix_audit_logs_org_id"))
            conn.commit()

        verifier = SchemaVerifier(migrated_database)
        verifier.verify_indexes()

        # Should have warning about missing index
        assert len(verifier.warnings) > 0
        assert any('ix_audit_logs_org_id' in warn.lower() for warn in verifier.warnings)

    def test_verifier_detects_wrong_primary_key(self, migrated_database, db_engine):
        """Test that verifier detects incorrect primary keys."""
        # This test creates a new table with wrong PK to test detection
        with db_engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS test_pk_table CASCADE"))
            conn.execute(text("""
                CREATE TABLE test_pk_table (
                    id TEXT,
                    name TEXT,
                    PRIMARY KEY (name)  -- Wrong PK
                )
            """))
            conn.commit()

        # Temporarily modify expected schema
        original_expected = SchemaVerifier.EXPECTED_PRIMARY_KEYS.copy()
        SchemaVerifier.EXPECTED_PRIMARY_KEYS['test_pk_table'] = ['id']  # We expect id, not name

        try:
            verifier = SchemaVerifier(migrated_database)
            verifier.verify_primary_keys()

            # Should have error about PK mismatch
            assert len(verifier.errors) > 0
            assert any('test_pk_table' in err for err in verifier.errors)
        finally:
            # Restore original
            SchemaVerifier.EXPECTED_PRIMARY_KEYS = original_expected

    def test_verifier_checks_alembic_version(self, migrated_database):
        """Test that verifier checks for alembic_version table."""
        verifier = SchemaVerifier(migrated_database)
        verifier.verify_alembic_version()

        # Should pass (migration was run)
        assert len(verifier.errors) == 0

    def test_verifier_warns_on_missing_alembic_version(self, clean_database, db_engine):
        """Test that verifier warns if alembic_version is missing."""
        # Create tables manually without alembic
        with db_engine.connect() as conn:
            conn.execute(text("CREATE TABLE orgs (id TEXT PRIMARY KEY)"))
            conn.commit()

        verifier = SchemaVerifier(clean_database)
        verifier.verify_alembic_version()

        # Should have warning
        assert len(verifier.warnings) > 0
        assert any('alembic' in warn.lower() for warn in verifier.warnings)

    def test_verifier_full_run(self, migrated_database):
        """Test complete verification run."""
        verifier = SchemaVerifier(migrated_database)
        success = verifier.verify_all()

        # Should pass completely
        assert success is True
        assert len(verifier.errors) == 0

    def test_verifier_returns_false_on_errors(self, migrated_database, db_engine):
        """Test that verifier returns False when errors exist."""
        # Drop a table to cause error
        with db_engine.connect() as conn:
            conn.execute(text("DROP TABLE users CASCADE"))
            conn.commit()

        verifier = SchemaVerifier(migrated_database)
        success = verifier.verify_all()

        # Should fail
        assert success is False
        assert len(verifier.errors) > 0

    def test_verifier_handles_connection_error(self):
        """Test that verifier handles connection errors gracefully."""
        invalid_url = "postgresql://invalid:invalid@localhost:9999/invalid"

        with pytest.raises(Exception):
            verifier = SchemaVerifier(invalid_url)
            verifier.verify_tables()
