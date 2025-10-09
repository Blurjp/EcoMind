"""
Tests for migration scripts (run_migrations.sh, baseline_database.sh)

These tests verify the logic and safety checks in migration automation scripts.
"""

import pytest
import subprocess
import os
from pathlib import Path


class TestMigrationScripts:
    """Test suite for migration automation scripts."""

    @pytest.fixture
    def scripts_dir(self):
        """Get path to scripts directory."""
        return Path(__file__).parent.parent.parent / "scripts"

    def test_run_migrations_help(self, scripts_dir):
        """Test that run_migrations.sh shows help."""
        script = scripts_dir / "run_migrations.sh"
        result = subprocess.run(
            [str(script), "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "Commands:" in result.stdout
        assert "upgrade" in result.stdout
        assert "downgrade" in result.stdout

    def test_run_migrations_requires_database_url(self, scripts_dir, monkeypatch):
        """Test that run_migrations.sh requires DATABASE_URL."""
        # Remove DATABASE_URL if set
        monkeypatch.delenv("DATABASE_URL", raising=False)

        script = scripts_dir / "run_migrations.sh"
        result = subprocess.run(
            [str(script), "check"],
            capture_output=True,
            text=True,
            env={"PATH": os.environ.get("PATH", "")}
        )

        assert result.returncode == 1
        assert "DATABASE_URL" in result.stdout or "DATABASE_URL" in result.stderr

    def test_baseline_help(self, scripts_dir):
        """Test that baseline_database.sh shows help."""
        script = scripts_dir / "baseline_database.sh"
        result = subprocess.run(
            [str(script), "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--undo" in result.stdout

    def test_baseline_requires_database_url(self, scripts_dir, monkeypatch):
        """Test that baseline_database.sh requires DATABASE_URL."""
        monkeypatch.delenv("DATABASE_URL", raising=False)

        script = scripts_dir / "baseline_database.sh"
        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True,
            env={"PATH": os.environ.get("PATH", "")}
        )

        assert result.returncode == 1
        assert "DATABASE_URL" in result.stdout or "DATABASE_URL" in result.stderr

    def test_scripts_are_executable(self, scripts_dir):
        """Test that scripts have executable permissions."""
        scripts = [
            "run_migrations.sh",
            "baseline_database.sh",
            "verify_schema.py"
        ]

        for script_name in scripts:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"{script_name} not found"
            assert os.access(script_path, os.X_OK), f"{script_name} not executable"

    def test_verify_schema_requires_database_url(self, scripts_dir, monkeypatch):
        """Test that verify_schema.py requires DATABASE_URL."""
        monkeypatch.delenv("DATABASE_URL", raising=False)

        script = scripts_dir / "verify_schema.py"
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            env={"PATH": os.environ.get("PATH", "")}
        )

        assert result.returncode == 1
        assert "DATABASE_URL" in result.stdout or "DATABASE_URL" in result.stderr


class TestAlembicConfiguration:
    """Test Alembic configuration."""

    def test_alembic_ini_exists(self):
        """Test that alembic.ini exists."""
        alembic_ini = Path(__file__).parent.parent.parent / "alembic.ini"
        assert alembic_ini.exists()

    def test_alembic_ini_no_hardcoded_credentials(self):
        """Test that alembic.ini doesn't contain hard-coded credentials."""
        alembic_ini = Path(__file__).parent.parent.parent / "alembic.ini"
        content = alembic_ini.read_text()

        # sqlalchemy.url should be empty (using environment variable)
        lines = content.split('\n')
        sqlalchemy_url_line = [l for l in lines if l.strip().startswith('sqlalchemy.url')]

        assert len(sqlalchemy_url_line) > 0, "sqlalchemy.url not found in alembic.ini"

        # Should be empty or just "sqlalchemy.url ="
        url_line = sqlalchemy_url_line[0]
        url_value = url_line.split('=', 1)[1].strip()

        assert url_value == "", \
            f"sqlalchemy.url should be empty (using env var), but got: {url_value}"

    def test_alembic_env_exists(self):
        """Test that alembic/env.py exists."""
        env_py = Path(__file__).parent.parent.parent / "alembic" / "env.py"
        assert env_py.exists()

    def test_alembic_env_uses_environment_variable(self):
        """Test that env.py reads DATABASE_URL from environment."""
        env_py = Path(__file__).parent.parent.parent / "alembic" / "env.py"
        content = env_py.read_text()

        assert "os.getenv" in content or "os.environ" in content
        assert "DATABASE_URL" in content

    def test_initial_migration_exists(self):
        """Test that initial migration file exists."""
        migration = Path(__file__).parent.parent.parent / "alembic" / "versions" / "001_initial_schema.py"
        assert migration.exists()

    def test_initial_migration_has_upgrade_and_downgrade(self):
        """Test that initial migration has both upgrade and downgrade."""
        migration = Path(__file__).parent.parent.parent / "alembic" / "versions" / "001_initial_schema.py"
        content = migration.read_text()

        assert "def upgrade()" in content
        assert "def downgrade()" in content

    def test_initial_migration_creates_all_tables(self):
        """Test that initial migration mentions all 8 tables."""
        migration = Path(__file__).parent.parent.parent / "alembic" / "versions" / "001_initial_schema.py"
        content = migration.read_text()

        expected_tables = [
            'orgs',
            'users',
            'events_enriched',
            'daily_org_agg',
            'daily_user_agg',
            'daily_provider_agg',
            'daily_model_agg',
            'audit_logs'
        ]

        for table in expected_tables:
            assert f"'{table}'" in content or f'"{table}"' in content, \
                f"Table {table} not found in migration"


class TestDocumentation:
    """Test that all documentation exists."""

    def test_secrets_documentation_exists(self):
        """Test that secrets.md documentation exists."""
        docs = Path(__file__).parent.parent.parent.parent / "docs" / "deployment" / "secrets.md"
        assert docs.exists()

    def test_secrets_documentation_covers_all_environments(self):
        """Test that documentation covers all environments."""
        docs = Path(__file__).parent.parent.parent.parent / "docs" / "deployment" / "secrets.md"
        content = docs.read_text()

        environments = [
            "Local Development",
            "Staging",
            "Production"
        ]

        for env in environments:
            assert env in content, f"Documentation missing {env} section"

    def test_secrets_documentation_covers_aws(self):
        """Test that documentation covers AWS Secrets Manager."""
        docs = Path(__file__).parent.parent.parent.parent / "docs" / "deployment" / "secrets.md"
        content = docs.read_text()

        assert "AWS Secrets Manager" in content
        assert "secretsmanager" in content.lower()

    def test_alembic_readme_exists(self):
        """Test that alembic README exists."""
        readme = Path(__file__).parent.parent.parent / "alembic" / "README"
        assert readme.exists()
