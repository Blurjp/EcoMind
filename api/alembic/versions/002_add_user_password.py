"""Add password field to users table

Revision ID: 002
Revises: 001
Create Date: 2025-10-08 00:30:00

This migration adds password hashing support to users table for Phase 2 (Authentication).

IMPORTANT: Existing users without passwords cannot login.
For production: Run a script to set initial passwords or use password reset flow.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash column to users table."""
    # Add password_hash column (nullable initially for existing users)
    op.add_column('users',
        sa.Column('password_hash', sa.String(), nullable=True)
    )

    # Note: In production, you would:
    # 1. Set temporary passwords for existing users
    # 2. Force password reset on first login
    # 3. Then make the column NOT NULL
    #
    # For now, we keep it nullable to not break existing data


def downgrade() -> None:
    """Remove password_hash column from users table."""
    op.drop_column('users', 'password_hash')
