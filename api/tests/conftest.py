"""
Pytest configuration and fixtures for EcoMind API tests.

This module provides shared fixtures for testing database migrations,
schema verification, and related infrastructure.
"""

import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for integration testing."""
    with PostgresContainer("postgres:15", driver="psycopg2") as postgres:
        # Wait for PostgreSQL to be ready
        postgres.get_connection_url()
        yield postgres


@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Get test database URL from container."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="function")
def clean_database(test_database_url):
    """Provide a clean database for each test."""
    engine = create_engine(test_database_url)

    # Drop all tables before test
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()

    yield test_database_url

    # Cleanup after test
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()

    engine.dispose()


@pytest.fixture
def db_engine(test_database_url):
    """Create a database engine for testing."""
    engine = create_engine(test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def set_test_env(test_database_url, monkeypatch):
    """Set DATABASE_URL environment variable for tests."""
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    yield test_database_url
