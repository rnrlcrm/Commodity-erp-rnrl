"""merge_migration_heads

Revision ID: 905a12a26853
Revises: 58286af88f2e, add_2fa_support, add_sub_user_support
Create Date: 2025-11-28 09:57:29.369949

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '905a12a26853'
down_revision = ('58286af88f2e', 'add_2fa_support', 'add_sub_user_support')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
