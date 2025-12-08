"""merge risk validations with other modules

Revision ID: 9c041691742c
Revises: 20251125_risk_validations, bdea096fec3e, create_requirement_engine
Create Date: 2025-11-25 07:26:41.537784

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '9c041691742c'
down_revision = ('20251125_risk_validations', 'bdea096fec3e', 'create_requirement_engine')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
