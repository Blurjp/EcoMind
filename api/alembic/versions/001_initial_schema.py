"""Initial schema - all 8 core tables

Revision ID: 001
Revises:
Create Date: 2025-10-07 22:40:00

This migration creates the initial schema for EcoMind, capturing all 8 core tables:
1. orgs - Organization management
2. users - User management with RBAC
3. events_enriched - Telemetry events with carbon footprint data
4. daily_org_agg - Daily aggregates by organization
5. daily_user_agg - Daily aggregates by user
6. daily_provider_agg - Daily aggregates by provider
7. daily_model_agg - Daily aggregates by model
8. audit_logs - Audit trail for security events

IMPORTANT FOR EXISTING DATABASES:
If you have an existing database with these tables, DO NOT run this migration directly.
Instead, use the baselining procedure:
  scripts/baseline_database.sh

This will mark the database as being at this revision without creating tables.
See: phases/P001/codex_review.md:293 (baselining strategy requirement)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables and indexes."""

    # 1. Create orgs table
    op.create_table(
        'orgs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('plan', sa.Enum('free', 'pro', 'enterprise', name='plantype'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('owner', 'admin', 'analyst', 'viewer', 'billing', name='role'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['orgs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 3. Create events_enriched table
    op.create_table(
        'events_enriched',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('tokens_in', sa.Integer(), nullable=True),
        sa.Column('tokens_out', sa.Integer(), nullable=True),
        sa.Column('node_type', sa.String(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('kwh', sa.Float(), nullable=False),
        sa.Column('water_l', sa.Float(), nullable=False),
        sa.Column('co2_kg', sa.Float(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_org_ts', 'events_enriched', ['org_id', 'ts'])
    op.create_index('ix_events_user_ts', 'events_enriched', ['user_id', 'ts'])
    op.create_index(op.f('ix_events_enriched_org_id'), 'events_enriched', ['org_id'])
    op.create_index(op.f('ix_events_enriched_ts'), 'events_enriched', ['ts'])
    op.create_index(op.f('ix_events_enriched_user_id'), 'events_enriched', ['user_id'])

    # 4. Create daily_org_agg table
    op.create_table(
        'daily_org_agg',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('call_count', sa.Integer(), nullable=True),
        sa.Column('kwh', sa.Float(), nullable=True),
        sa.Column('water_l', sa.Float(), nullable=True),
        sa.Column('co2_kg', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('date', 'org_id')
    )
    op.create_index('ix_daily_org_date', 'daily_org_agg', ['date', 'org_id'])

    # 5. Create daily_user_agg table
    op.create_table(
        'daily_user_agg',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('call_count', sa.Integer(), nullable=True),
        sa.Column('kwh', sa.Float(), nullable=True),
        sa.Column('water_l', sa.Float(), nullable=True),
        sa.Column('co2_kg', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('date', 'org_id', 'user_id')
    )

    # 6. Create daily_provider_agg table
    op.create_table(
        'daily_provider_agg',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('call_count', sa.Integer(), nullable=True),
        sa.Column('kwh', sa.Float(), nullable=True),
        sa.Column('water_l', sa.Float(), nullable=True),
        sa.Column('co2_kg', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('date', 'org_id', 'provider')
    )

    # 7. Create daily_model_agg table
    op.create_table(
        'daily_model_agg',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('call_count', sa.Integer(), nullable=True),
        sa.Column('kwh', sa.Float(), nullable=True),
        sa.Column('water_l', sa.Float(), nullable=True),
        sa.Column('co2_kg', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('date', 'org_id', 'provider', 'model')
    )

    # 8. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource', sa.String(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ts', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_org_id'), 'audit_logs', ['org_id'])
    op.create_index(op.f('ix_audit_logs_ts'), 'audit_logs', ['ts'])


def downgrade() -> None:
    """Drop all tables and indexes.

    WARNING: This will delete all data!
    Only use for development or in rollback scenarios where data loss is acceptable.
    """
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index(op.f('ix_audit_logs_ts'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_org_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_table('daily_model_agg')
    op.drop_table('daily_provider_agg')
    op.drop_table('daily_user_agg')

    op.drop_index('ix_daily_org_date', table_name='daily_org_agg')
    op.drop_table('daily_org_agg')

    op.drop_index(op.f('ix_events_enriched_user_id'), table_name='events_enriched')
    op.drop_index(op.f('ix_events_enriched_ts'), table_name='events_enriched')
    op.drop_index(op.f('ix_events_enriched_org_id'), table_name='events_enriched')
    op.drop_index('ix_events_user_ts', table_name='events_enriched')
    op.drop_index('ix_events_org_ts', table_name='events_enriched')
    op.drop_table('events_enriched')

    op.drop_table('users')
    op.drop_table('orgs')
