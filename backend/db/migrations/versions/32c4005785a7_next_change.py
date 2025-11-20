"""next-change

Revision ID: 32c4005785a7
Revises: eaf12a4e04a0
Create Date: 2025-11-19 15:19:22.405631

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '32c4005785a7'
down_revision = 'eaf12a4e04a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: constraints already exist from baseline.
    pass


def downgrade() -> None:
    # No-op: nothing to revert.
    pass
