"""create_partner_onboarding_tables

Revision ID: cf052225ae84
Revises: 11c028f561fb
Create Date: 2025-11-22 11:33:17.964895

Creates 8 tables for business partner onboarding and management:
1. business_partners - Main partner table
2. partner_locations - Additional locations/branches
3. partner_employees - Partner employees (max 2)
4. partner_documents - Uploaded documents with OCR
5. partner_vehicles - Transporter vehicles
6. partner_onboarding_applications - Temporary onboarding applications
7. partner_amendments - Post-approval amendments
8. partner_kyc_renewals - Yearly KYC renewal tracking

Data Isolation:
- business_partners: organization_id (settings table)
- Child tables: partner_id FK + organization_id
- EXTERNAL users filtered by partner_id (from get_current_business_partner_id())

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'cf052225ae84'
down_revision = '11c028f561fb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all partner onboarding tables (business_partners already exists from previous migration)"""
    
    # NOTE: business_partners table created in migration 59d2e1f64664
    # This migration only creates the onboarding-related tables
    
    # 2. Partner Locations
    op.create_table(
        'partner_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('location_type', sa.String(50), nullable=False),
        sa.Column('location_name', sa.String(200), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False),
        
        # GST for this location
        sa.Column('is_from_gst', sa.Boolean(), default=False),
        sa.Column('gstin_for_location', sa.String(15), nullable=True),
        sa.Column('requires_gst', sa.Boolean(), default=True),
        
        # Address
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=False),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('latitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('longitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('location_geocoded', sa.Boolean(), default=False),
        sa.Column('location_confidence', sa.Numeric(3, 2), nullable=True),
        
        # Soft delete
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    op.create_index('ix_partner_locations_partner_id', 'partner_locations', ['partner_id'])
    op.create_index('ix_partner_locations_organization_id', 'partner_locations', ['organization_id'])
    
    # 3. Partner Employees
    op.create_table(
        'partner_employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('employee_name', sa.String(200), nullable=False),
        sa.Column('employee_email', sa.String(200), nullable=False),
        sa.Column('employee_phone', sa.String(20), nullable=False),
        sa.Column('designation', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), default='employee'),
        sa.Column('permissions', postgresql.JSON, nullable=True),
        
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        
        # Soft delete
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    op.create_index('ix_partner_employees_partner_id', 'partner_employees', ['partner_id'])
    op.create_index('ix_partner_employees_user_id', 'partner_employees', ['user_id'])
    
    # 4. Partner Documents
    op.create_table(
        'partner_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('document_type', sa.String(100), nullable=False),
        sa.Column('document_subtype', sa.String(100), nullable=True),
        sa.Column('file_url', sa.String(1000), nullable=False),
        sa.Column('file_name', sa.String(500)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        
        # OCR extraction
        sa.Column('ocr_extracted_data', postgresql.JSON, nullable=True),
        sa.Column('ocr_confidence', sa.Numeric(3, 2), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        
        # Soft delete
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    op.create_index('ix_partner_documents_partner_id', 'partner_documents', ['partner_id'])
    op.create_index('ix_partner_documents_type', 'partner_documents', ['document_type'])
    
    # 5. Partner Vehicles (for transporters)
    op.create_table(
        'partner_vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('registration_number', sa.String(50), nullable=False),
        sa.Column('vehicle_type', sa.String(100), nullable=False),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('year_of_manufacture', sa.Integer(), nullable=True),
        sa.Column('capacity_tons', sa.Numeric(10, 2), nullable=True),
        
        # RTO Verification
        sa.Column('rto_verified', sa.Boolean(), default=False),
        sa.Column('rto_verification_data', postgresql.JSON, nullable=True),
        sa.Column('rto_verified_at', sa.DateTime(timezone=True), nullable=True),
        
        # Insurance & Fitness
        sa.Column('insurance_valid_until', sa.Date(), nullable=True),
        sa.Column('fitness_valid_until', sa.Date(), nullable=True),
        sa.Column('permit_type', sa.String(100), nullable=True),
        
        sa.Column('is_active', sa.Boolean(), default=True),
        
        # Soft delete
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    op.create_index('ix_partner_vehicles_partner_id', 'partner_vehicles', ['partner_id'])
    op.create_index('ix_partner_vehicles_registration', 'partner_vehicles', ['registration_number'])
    op.create_unique_constraint('uq_vehicle_registration', 'partner_vehicles', ['registration_number'])
    
    # 6. Partner Onboarding Applications (temporary table)
    op.create_table(
        'partner_onboarding_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Same fields as business_partners
        sa.Column('partner_type', sa.String(50), nullable=False),
        sa.Column('legal_business_name', sa.String(500), nullable=False),
        sa.Column('trade_name', sa.String(500), nullable=True),
        sa.Column('tax_id_number', sa.String(15), nullable=False),
        sa.Column('pan_number', sa.String(10), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('business_registration_date', sa.Date(), nullable=True),
        
        sa.Column('primary_address', sa.Text(), nullable=False),
        sa.Column('primary_city', sa.String(100), nullable=False),
        sa.Column('primary_state', sa.String(100), nullable=True),
        sa.Column('primary_postal_code', sa.String(20), nullable=False),
        sa.Column('primary_country', sa.String(100), nullable=False),
        sa.Column('primary_latitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('primary_longitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('location_geocoded', sa.Boolean(), default=False),
        sa.Column('location_confidence', sa.Numeric(3, 2), nullable=True),
        
        sa.Column('primary_contact_person', sa.String(200), nullable=False),
        sa.Column('primary_contact_email', sa.String(200), nullable=False),
        sa.Column('primary_contact_phone', sa.String(20), nullable=False),
        
        # Verification status
        sa.Column('gst_verified', sa.Boolean(), default=False),
        sa.Column('gst_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gst_verification_data', postgresql.JSON, nullable=True),
        sa.Column('pan_verified', sa.Boolean(), default=False),
        sa.Column('location_verified', sa.Boolean(), default=False),
        sa.Column('documents_count', sa.Integer(), default=0),
        
        # Risk
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_category', sa.String(20), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
    )
    
    op.create_index('ix_onboarding_apps_organization_id', 'partner_onboarding_applications', ['organization_id'])
    op.create_index('ix_onboarding_apps_status', 'partner_onboarding_applications', ['status'])
    
    # 7. Partner Amendments
    op.create_table(
        'partner_amendments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('amendment_type', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('supporting_documents', postgresql.JSON, nullable=True),
        
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
    )
    
    op.create_index('ix_partner_amendments_partner_id', 'partner_amendments', ['partner_id'])
    op.create_index('ix_partner_amendments_status', 'partner_amendments', ['status'])
    
    # 8. Partner KYC Renewals
    op.create_table(
        'partner_kyc_renewals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verification_passed', sa.Boolean(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        
        sa.Column('new_documents', postgresql.JSON, nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['business_partners.id'], ondelete='CASCADE'),
    )
    
    op.create_index('ix_partner_kyc_renewals_partner_id', 'partner_kyc_renewals', ['partner_id'])
    op.create_index('ix_partner_kyc_renewals_status', 'partner_kyc_renewals', ['status'])
    op.create_index('ix_partner_kyc_renewals_due_date', 'partner_kyc_renewals', ['due_date'])


def downgrade() -> None:
    """Drop all partner onboarding tables"""
    op.drop_table('partner_kyc_renewals')
    op.drop_table('partner_amendments')
    op.drop_table('partner_onboarding_applications')
    op.drop_table('partner_vehicles')
    op.drop_table('partner_documents')
    op.drop_table('partner_employees')
    op.drop_table('partner_locations')
    op.drop_table('business_partners')

