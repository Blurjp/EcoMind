"""
Tests for initial migration (001_initial_schema.py)

Verifies that the initial migration correctly creates all 8 tables
with proper columns, constraints, and indexes.
"""

import pytest
from sqlalchemy import inspect, text
from alembic import command
from alembic.config import Config
import os


class TestInitialMigration:
    """Test suite for initial database migration."""

    @pytest.fixture
    def alembic_config(self, set_test_env):
        """Create Alembic configuration for testing."""
        config = Config("alembic.ini")
        config.set_main_option("script_location", "alembic")
        config.set_main_option("sqlalchemy.url", set_test_env)
        return config

    def test_upgrade_creates_all_tables(self, clean_database, alembic_config, db_engine):
        """Test that upgrade creates all 8 expected tables."""
        # Run migration
        command.upgrade(alembic_config, "head")

        # Verify tables exist
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()

        expected_tables = {
            'orgs',
            'users',
            'events_enriched',
            'daily_org_agg',
            'daily_user_agg',
            'daily_provider_agg',
            'daily_model_agg',
            'audit_logs',
            'alembic_version'
        }

        assert set(tables) == expected_tables, f"Missing tables: {expected_tables - set(tables)}"

    def test_orgs_table_structure(self, clean_database, alembic_config, db_engine):
        """Test organizations table structure."""
        command.upgrade(alembic_config, "head")
        inspector = inspect(db_engine)

        # Check columns
        columns = {col['name']: col for col in inspector.get_columns('orgs')}
        assert 'id' in columns
        assert 'name' in columns
        assert 'plan' in columns
        assert 'created_at' in columns

        # Check primary key
        pk = inspector.get_pk_constraint('orgs')
        assert pk['constrained_columns'] == ['id']

    def test_users_table_structure(self, clean_database, alembic_config, db_engine):
        """Test users table structure."""
        command.upgrade(alembic_config, "head")
        inspector = inspect(db_engine)

        # Check columns
        columns = {col['name']: col for col in inspector.get_columns('users')}
        assert 'id' in columns
        assert 'org_id' in columns
        assert 'email' in columns
        assert 'role' in columns

        # Check primary key
        pk = inspector.get_pk_constraint('users')
        assert pk['constrained_columns'] == ['id']

        # Check foreign key
        fks = inspector.get_foreign_keys('users')
        assert len(fks) == 1
        assert fks[0]['referred_table'] == 'orgs'
        assert fks[0]['referred_columns'] == ['id']

        # Check unique constraint on email
        unique_constraints = inspector.get_unique_constraints('users')
        email_unique = any('email' in uc['column_names'] for uc in unique_constraints)
        assert email_unique, "Email should have unique constraint"

    def test_events_enriched_table_structure(self, clean_database, alembic_config, db_engine):
        """Test events_enriched table structure."""
        command.upgrade(alembic_config, "head")
        inspector = inspect(db_engine)

        columns = {col['name']: col for col in inspector.get_columns('events_enriched')}

        # Check critical columns
        required_columns = [
            'id', 'org_id', 'user_id', 'provider', 'model',
            'tokens_in', 'tokens_out', 'kwh', 'water_l', 'co2_kg',
            'ts', 'metadata', 'created_at'
        ]
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"

        # Check indexes
        indexes = inspector.get_indexes('events_enriched')
        index_names = {idx['name'] for idx in indexes}

        expected_indexes = {
            'ix_events_org_ts',
            'ix_events_user_ts',
            'ix_events_enriched_org_id',
            'ix_events_enriched_ts',
            'ix_events_enriched_user_id'
        }

        assert expected_indexes.issubset(index_names), \
            f"Missing indexes: {expected_indexes - index_names}"

    def test_daily_aggregation_tables(self, clean_database, alembic_config, db_engine):
        """Test all daily aggregation tables."""
        command.upgrade(alembic_config, "head")
        inspector = inspect(db_engine)

        agg_tables = {
            'daily_org_agg': ['date', 'org_id'],
            'daily_user_agg': ['date', 'org_id', 'user_id'],
            'daily_provider_agg': ['date', 'org_id', 'provider'],
            'daily_model_agg': ['date', 'org_id', 'provider', 'model'],
        }

        for table_name, pk_cols in agg_tables.items():
            # Check table exists
            assert table_name in inspector.get_table_names()

            # Check primary key
            pk = inspector.get_pk_constraint(table_name)
            assert set(pk['constrained_columns']) == set(pk_cols), \
                f"{table_name} PK mismatch"

            # Check metric columns exist
            columns = {col['name'] for col in inspector.get_columns(table_name)}
            for metric in ['call_count', 'kwh', 'water_l', 'co2_kg']:
                assert metric in columns, f"{table_name} missing {metric}"

    def test_audit_logs_table_structure(self, clean_database, alembic_config, db_engine):
        """Test audit_logs table structure."""
        command.upgrade(alembic_config, "head")
        inspector = inspect(db_engine)

        columns = {col['name']: col for col in inspector.get_columns('audit_logs')}

        required_columns = ['id', 'org_id', 'user_id', 'action', 'resource', 'details', 'ts']
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"

        # Check indexes
        indexes = inspector.get_indexes('audit_logs')
        index_names = {idx['name'] for idx in indexes}
        assert 'ix_audit_logs_org_id' in index_names
        assert 'ix_audit_logs_ts' in index_names

    def test_downgrade_removes_all_tables(self, clean_database, alembic_config, db_engine):
        """Test that downgrade removes all tables."""
        # Upgrade first
        command.upgrade(alembic_config, "head")

        # Verify tables exist
        inspector = inspect(db_engine)
        tables_before = set(inspector.get_table_names())
        assert len(tables_before) >= 8

        # Downgrade
        command.downgrade(alembic_config, "base")

        # Verify tables removed (except alembic_version might remain)
        tables_after = set(inspector.get_table_names())
        expected_removed = {
            'orgs', 'users', 'events_enriched',
            'daily_org_agg', 'daily_user_agg',
            'daily_provider_agg', 'daily_model_agg',
            'audit_logs'
        }

        remaining = expected_removed & tables_after
        assert len(remaining) == 0, f"Tables not removed: {remaining}"

    def test_migration_is_idempotent(self, clean_database, alembic_config, db_engine):
        """Test that running migration twice doesn't cause errors."""
        # First migration
        command.upgrade(alembic_config, "head")

        # Get table count
        inspector = inspect(db_engine)
        tables_first = set(inspector.get_table_names())

        # Running upgrade again should be safe (already at head)
        command.upgrade(alembic_config, "head")

        tables_second = set(inspector.get_table_names())
        assert tables_first == tables_second

    def test_alembic_version_table(self, clean_database, alembic_config, db_engine):
        """Test that alembic_version table is created and populated."""
        command.upgrade(alembic_config, "head")

        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()

            assert version is not None
            assert version[0] == '001'  # Initial migration version

    def test_can_insert_data_after_migration(self, clean_database, alembic_config, db_engine):
        """Test that we can insert data into migrated tables."""
        command.upgrade(alembic_config, "head")

        with db_engine.connect() as conn:
            # Insert org
            conn.execute(text("""
                INSERT INTO orgs (id, name, plan, created_at)
                VALUES ('org_test123', 'Test Org', 'FREE', NOW())
            """))

            # Insert user
            conn.execute(text("""
                INSERT INTO users (id, org_id, email, role, created_at)
                VALUES ('user_test123', 'org_test123', 'test@example.com', 'VIEWER', NOW())
            """))

            # Verify data
            result = conn.execute(text("SELECT COUNT(*) FROM orgs"))
            assert result.fetchone()[0] == 1

            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            assert result.fetchone()[0] == 1

            conn.commit()

    def test_foreign_key_constraint_works(self, clean_database, alembic_config, db_engine):
        """Test that foreign key constraints are enforced."""
        command.upgrade(alembic_config, "head")

        with pytest.raises(Exception) as exc_info:
            with db_engine.connect() as conn:
                # Try to insert user without org (should fail)
                conn.execute(text("""
                    INSERT INTO users (id, org_id, email, role)
                    VALUES ('user_test', 'nonexistent_org', 'test@example.com', 'VIEWER')
                """))
                conn.commit()

        assert "foreign key" in str(exc_info.value).lower() or "violates" in str(exc_info.value).lower()
