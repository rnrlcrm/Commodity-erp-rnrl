"""create_business_partners_table

Complete Business Partner model for data isolation and onboarding.
This is the authoritative business_partners table creation - all columns defined here.

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
    # Create business_partners table with full schema
    op.create_table(
        'business_partners',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Partner Type
        sa.Column('partner_type', sa.String(50), nullable=False, comment='seller, buyer, trader, broker, sub_broker, transporter, controller, financer, shipping_agent, importer, exporter'),
        sa.Column('service_provider_type', sa.String(50), nullable=True),
        sa.Column('trade_classification', sa.String(50), nullable=True, comment='domestic, exporter, importer'),
        
        # Business Details
        sa.Column('legal_business_name', sa.String(500), nullable=False),
        sa.Column('trade_name', sa.String(500), nullable=True),
        sa.Column('tax_id_number', sa.String(15), nullable=False, comment='GSTIN'),
        sa.Column('pan_number', sa.String(10), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('business_registration_number', sa.String(100), nullable=True),
        sa.Column('business_registration_date', sa.Date(), nullable=True),
        
        # Address
        sa.Column('primary_address', sa.Text(), nullable=False),
        sa.Column('primary_city', sa.String(100), nullable=False),
        sa.Column('primary_state', sa.String(100), nullable=True),
        sa.Column('primary_postal_code', sa.String(20), nullable=False),
        sa.Column('primary_country', sa.String(100), nullable=False),
        sa.Column('primary_latitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('primary_longitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('location_geocoded', sa.Boolean(), default=False),
        sa.Column('location_confidence', sa.Numeric(3, 2), nullable=True),
        
        # Contact
        sa.Column('primary_contact_person', sa.String(200), nullable=False),
        sa.Column('primary_contact_email', sa.String(200), nullable=False),
        sa.Column('primary_contact_phone', sa.String(20), nullable=False),
        sa.Column('primary_currency', sa.String(3), default='INR'),
        
        # Buyer-specific
        sa.Column('credit_limit', sa.Numeric(20, 2), nullable=True),
        sa.Column('credit_utilized', sa.Numeric(20, 2), default=0),
        sa.Column('payment_terms_days', sa.Integer(), nullable=True),
        sa.Column('monthly_purchase_volume', sa.String(100), nullable=True),
        
        # Seller-specific
        sa.Column('production_capacity', sa.String(200), nullable=True),
        sa.Column('can_arrange_transport', sa.Boolean(), default=False),
        sa.Column('has_quality_lab', sa.Boolean(), default=False),
        
        # Service provider details (JSON)
        sa.Column('service_details', postgresql.JSON, nullable=True),
        sa.Column('commodities', postgresql.JSON, nullable=True),
        
        # Risk Assessment
        sa.Column('risk_score', sa.Integer(), nullable=True, comment='0-100'),
        sa.Column('risk_category', sa.String(20), nullable=True, comment='low, medium, high, critical'),
        sa.Column('risk_assessment', postgresql.JSON, nullable=True),
        sa.Column('last_risk_assessment_at', sa.DateTime(timezone=True), nullable=True),
        
        # KYC
        sa.Column('kyc_status', sa.String(20), default='pending'),
        sa.Column('kyc_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('kyc_expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('kyc_last_renewed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Employees
        sa.Column('max_employees_allowed', sa.Integer(), default=2),
        sa.Column('current_employee_count', sa.Integer(), default=0),
        
        # Status
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        
        # Soft delete (GDPR 7-year retention)
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    # Create indexes for performance
    op.create_index('ix_business_partners_organization_id', 'business_partners', ['organization_id'])
    op.create_index('ix_business_partners_partner_type', 'business_partners', ['partner_type'])
    op.create_index('ix_business_partners_tax_id', 'business_partners', ['tax_id_number'])
    op.create_index('ix_business_partners_pan', 'business_partners', ['pan_number'])
    op.create_index('ix_business_partners_status', 'business_partners', ['status'])
    op.create_index('ix_business_partners_kyc_status', 'business_partners', ['kyc_status'])
    op.create_index('ix_business_partners_kyc_expiry', 'business_partners', ['kyc_expiry_date'])
    op.create_index('ix_business_partners_is_deleted', 'business_partners', ['is_deleted'])
    
    # Unique constraint
    op.create_unique_constraint('uq_partners_org_tax_id', 'business_partners', ['organization_id', 'tax_id_number'])


def downgrade() -> None:
    # Drop unique constraint
    op.drop_constraint('uq_partners_org_tax_id', 'business_partners', type_='unique')
    
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS ix_business_partners_is_deleted')
op.execute('DROP INDEX IF EXISTS ix_business_partners_kyc_expiry')
op.execute('DROP INDEX IF EXISTS ix_business_partners_kyc_status')
op.execute('DROP INDEX IF EXISTS ix_business_partners_status')
op.execute('DROP INDEX IF EXISTS ix_business_partners_pan')
op.execute('DROP INDEX IF EXISTS ix_business_partners_tax_id')
op.execute('DROP INDEX IF EXISTS ix_business_partners_partner_type')
op.execute('DROP INDEX IF EXISTS ix_business_partners_organization_id')
# Drop table
    op.drop_table('business_partners')
