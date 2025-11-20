"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = '${up_revision}'
% if down_revision is None:
down_revision = None
% else:
down_revision = '${down_revision}'
% endif
% if branch_labels is None:
branch_labels = None
% else:
branch_labels = ${branch_labels | repr}
% endif
% if depends_on is None:
depends_on = None
% else:
depends_on = ${depends_on | repr}
% endif


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
