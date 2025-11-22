"""create_business_partners_table

Minimal Business Partner model for data isolation FK foundation.
Full business partner features will be added in dedicated module later.

Revision ID: 59d2e1f64664
Revises: 025fe632dacf
Create Date: 2025-11-22 06:10:55.400503

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '59d2e1f64664'
down_revision = '025fe632dacf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create business_partners table
    op.create_table(
        'business_partners',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('partner_type', sa.String(50), nullable=False, comment='BUYER, SELLER, BROKER, TRANSPORTER, BOTH'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deletion_reason', sa.Text(), nullable=True),
    )
    
    # Create indexes for performance
    op.create_index(
        'ix_business_partners_name',
        'business_partners',
        ['name']
    )
    op.create_index(
        'ix_business_partners_partner_type',
        'business_partners',
        ['partner_type'],
        postgresql_where=sa.text('is_deleted = false')
    )
    op.create_index(
        'ix_business_partners_is_active',
        'business_partners',
        ['is_active'],
        postgresql_where=sa.text('is_deleted = false')
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_business_partners_is_active', table_name='business_partners')
    op.drop_index('ix_business_partners_partner_type', table_name='business_partners')
    op.drop_index('ix_business_partners_name', table_name='business_partners')
    
    # Drop table
    op.drop_table('business_partners')
