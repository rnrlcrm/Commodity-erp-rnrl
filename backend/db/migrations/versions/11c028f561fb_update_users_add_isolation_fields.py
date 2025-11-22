"""update_users_add_isolation_fields

Add data isolation fields to users table:
- user_type (SUPER_ADMIN, INTERNAL, EXTERNAL)
- business_partner_id FK (for EXTERNAL users)
- organization_id FK made nullable (for INTERNAL users)
- allowed_modules array (for RBAC)
- CHECK constraint to enforce isolation rules

Revision ID: 11c028f561fb
Revises: 59d2e1f64664
Create Date: 2025-11-22 06:12:09.562663

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '11c028f561fb'
down_revision = '59d2e1f64664'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column(
        'users',
        sa.Column('user_type', sa.String(20), nullable=False, server_default='INTERNAL', comment='SUPER_ADMIN, INTERNAL, or EXTERNAL')
    )
    op.add_column(
        'users',
        sa.Column('business_partner_id', postgresql.UUID(as_uuid=True), nullable=True, comment='For EXTERNAL users only')
    )
    op.add_column(
        'users',
        sa.Column('allowed_modules', postgresql.ARRAY(sa.String()), nullable=True, comment='RBAC: List of modules user can access')
    )
    
    # Make organization_id nullable (was NOT NULL before)
    op.alter_column('users', 'organization_id', nullable=True)
    
    # Add foreign key to business_partners
    op.create_foreign_key(
        'fk_users_business_partner',
        'users',
        'business_partners',
        ['business_partner_id'],
        ['id'],
        ondelete='RESTRICT'
    )
    
    # Add CHECK constraint for data isolation rules
    op.create_check_constraint(
        'ck_user_type_isolation',
        'users',
        """
        (user_type = 'SUPER_ADMIN' AND business_partner_id IS NULL AND organization_id IS NULL) OR
        (user_type = 'INTERNAL' AND business_partner_id IS NULL AND organization_id IS NOT NULL) OR
        (user_type = 'EXTERNAL' AND business_partner_id IS NOT NULL AND organization_id IS NULL)
        """
    )
    
    # Create indexes for performance
    op.create_index(
        'ix_users_user_type',
        'users',
        ['user_type']
    )
    op.create_index(
        'ix_users_business_partner_id',
        'users',
        ['business_partner_id'],
        postgresql_where=sa.text('business_partner_id IS NOT NULL')
    )
    op.create_index(
        'ix_users_organization_id',
        'users',
        ['organization_id'],
        postgresql_where=sa.text('organization_id IS NOT NULL')
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_users_organization_id', table_name='users')
    op.drop_index('ix_users_business_partner_id', table_name='users')
    op.drop_index('ix_users_user_type', table_name='users')
    
    # Drop constraint
    op.drop_constraint('ck_user_type_isolation', 'users', type_='check')
    
    # Drop foreign key
    op.drop_constraint('fk_users_business_partner', 'users', type_='foreignkey')
    
    # Make organization_id NOT NULL again
    op.alter_column('users', 'organization_id', nullable=False)
    
    # Drop columns
    op.drop_column('users', 'allowed_modules')
    op.drop_column('users', 'business_partner_id')
    op.drop_column('users', 'user_type')
