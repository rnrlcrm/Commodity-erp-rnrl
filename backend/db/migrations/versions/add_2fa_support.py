"""add 2FA support with PIN authentication

Revision ID: add_2fa_support
Revises: 
Create Date: 2025-11-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_2fa_support'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add two_fa_enabled and pin_hash columns to users table."""
    op.add_column('users', sa.Column('two_fa_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('pin_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove 2FA columns from users table."""
    op.drop_column('users', 'pin_hash')
    op.drop_column('users', 'two_fa_enabled')
