"""create organization settings

Revision ID: 20251120_1400
Revises: eaf12a4e04a0
Create Date: 2025-11-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251120_1400'
down_revision = 'eaf12a4e04a0'
branch_labels = None
depends_on = None


def upgrade():
    # Extend existing organizations table with new columns
    op.add_column('organizations', sa.Column('legal_name', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('type', sa.String(64), nullable=True))
    op.add_column('organizations', sa.Column('CIN', sa.String(21), nullable=True))
    op.add_column('organizations', sa.Column('PAN', sa.String(10), nullable=True))
    op.add_column('organizations', sa.Column('base_currency', sa.String(3), nullable=False, server_default='INR'))
    op.add_column('organizations', sa.Column('address_line1', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('address_line2', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('city', sa.String(128), nullable=True))
    op.add_column('organizations', sa.Column('state', sa.String(128), nullable=True))
    op.add_column('organizations', sa.Column('pincode', sa.String(16), nullable=True))
    op.add_column('organizations', sa.Column('contact_email', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('contact_phone', sa.String(32), nullable=True))
    op.add_column('organizations', sa.Column('threshold_limit', sa.Integer(), nullable=True))
    op.add_column('organizations', sa.Column('einvoice_required', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('auto_block_if_einvoice_required', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('fx_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('logo_url', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('theme_color', sa.String(64), nullable=True))
    op.add_column('organizations', sa.Column('invoice_footer', sa.String(1024), nullable=True))
    op.add_column('organizations', sa.Column('digital_signature_url', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('tds_rate', sa.Integer(), nullable=True))
    op.add_column('organizations', sa.Column('tcs_rate', sa.Integer(), nullable=True))
    op.add_column('organizations', sa.Column('audit_firm_name', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('audit_firm_email', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('audit_firm_phone', sa.String(32), nullable=True))
    op.add_column('organizations', sa.Column('gst_audit_required', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('auto_invoice', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('auto_contract_number', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('extra_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    
    # Drop the 'code' column if it exists (not in new schema)
    op.drop_column('organizations', 'code')

    # Create organization_gst table
    op.create_table(
        'organization_gst',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gstin', sa.String(15), nullable=False, unique=True),
        sa.Column('legal_name', sa.String(255), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('state', sa.String(128), nullable=True),
        sa.Column('branch_code', sa.String(32), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_organization_gst_gstin', 'organization_gst', ['gstin'])
    op.create_index('ix_organization_gst_organization_id', 'organization_gst', ['organization_id'])
    op.create_index('ix_organization_gst_is_primary', 'organization_gst', ['is_primary'])

    # Create organization_bank_accounts table
    op.create_table(
        'organization_bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_holder', sa.String(255), nullable=False),
        sa.Column('bank_name', sa.String(255), nullable=False),
        sa.Column('account_number', sa.String(64), nullable=False),
        sa.Column('ifsc', sa.String(11), nullable=True),
        sa.Column('branch', sa.String(255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_organization_bank_accounts_organization_id', 'organization_bank_accounts', ['organization_id'])
    op.create_index('ix_organization_bank_accounts_is_default', 'organization_bank_accounts', ['is_default'])

    # Create organization_financial_years table
    op.create_table(
        'organization_financial_years',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allow_year_split', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_organization_financial_years_organization_id', 'organization_financial_years', ['organization_id'])
    op.create_index('ix_organization_financial_years_start_date', 'organization_financial_years', ['start_date'])
    op.create_index('ix_organization_financial_years_end_date', 'organization_financial_years', ['end_date'])
    op.create_index('ix_organization_financial_years_is_active', 'organization_financial_years', ['is_active'])

    # Create organization_document_series table
    op.create_table(
        'organization_document_series',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('financial_year_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organization_financial_years.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String(64), nullable=False),
        sa.Column('prefix', sa.String(32), nullable=True),
        sa.Column('current_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reset_annually', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('extra_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('organization_id', 'document_type', 'financial_year_id', name='uq_org_doc_series'),
    )
    op.create_index('ix_organization_document_series_organization_id', 'organization_document_series', ['organization_id'])
    op.create_index('ix_organization_document_series_financial_year_id', 'organization_document_series', ['financial_year_id'])
    op.create_index('ix_organization_document_series_document_type', 'organization_document_series', ['document_type'])


def downgrade():
    op.execute('DROP INDEX IF EXISTS ix_organization_document_series_document_type')
op.execute('DROP INDEX IF EXISTS ix_organization_document_series_financial_year_id')
op.execute('DROP INDEX IF EXISTS ix_organization_document_series_organization_id')
op.drop_table('organization_document_series')

    op.execute('DROP INDEX IF EXISTS ix_organization_financial_years_is_active')
op.execute('DROP INDEX IF EXISTS ix_organization_financial_years_end_date')
op.execute('DROP INDEX IF EXISTS ix_organization_financial_years_start_date')
op.execute('DROP INDEX IF EXISTS ix_organization_financial_years_organization_id')
op.drop_table('organization_financial_years')

    op.execute('DROP INDEX IF EXISTS ix_organization_bank_accounts_is_default')
op.execute('DROP INDEX IF EXISTS ix_organization_bank_accounts_organization_id')
op.drop_table('organization_bank_accounts')

    op.execute('DROP INDEX IF EXISTS ix_organization_gst_is_primary')
op.execute('DROP INDEX IF EXISTS ix_organization_gst_organization_id')
op.execute('DROP INDEX IF EXISTS ix_organization_gst_gstin')
op.drop_table('organization_gst')

    # Restore organizations table to original state
    op.add_column('organizations', sa.Column('code', sa.String(64), nullable=True, unique=True))
    op.drop_column('organizations', 'extra_config')
    op.drop_column('organizations', 'auto_contract_number')
    op.drop_column('organizations', 'auto_invoice')
    op.drop_column('organizations', 'gst_audit_required')
    op.drop_column('organizations', 'audit_firm_phone')
    op.drop_column('organizations', 'audit_firm_email')
    op.drop_column('organizations', 'audit_firm_name')
    op.drop_column('organizations', 'tcs_rate')
    op.drop_column('organizations', 'tds_rate')
    op.drop_column('organizations', 'digital_signature_url')
    op.drop_column('organizations', 'invoice_footer')
    op.drop_column('organizations', 'theme_color')
    op.drop_column('organizations', 'logo_url')
    op.drop_column('organizations', 'fx_enabled')
    op.drop_column('organizations', 'auto_block_if_einvoice_required')
    op.drop_column('organizations', 'einvoice_required')
    op.drop_column('organizations', 'threshold_limit')
    op.drop_column('organizations', 'contact_phone')
    op.drop_column('organizations', 'contact_email')
    op.drop_column('organizations', 'pincode')
    op.drop_column('organizations', 'state')
    op.drop_column('organizations', 'city')
    op.drop_column('organizations', 'address_line2')
    op.drop_column('organizations', 'address_line1')
    op.drop_column('organizations', 'base_currency')
    op.drop_column('organizations', 'PAN')
    op.drop_column('organizations', 'CIN')
    op.drop_column('organizations', 'type')
    op.drop_column('organizations', 'legal_name')


# Do not assume or invent anything. Only implement EXACTLY what is written here and in the models.
