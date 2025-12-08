"""cdps_capability_driven_partner_system

Capability-Driven Partner System (CDPS) Migration

This migration adds:
1. New columns: entity_class, capabilities, master_entity_id, corporate_group_id, is_master_entity, entity_hierarchy
2. Data conversion from partner_type → entity_class + capabilities
3. CRITICAL: Foreign entities get home_country capabilities ONLY (NOT India capabilities)

Revision ID: b6d57334a17e
Revises: 905a12a26853
Create Date: 2025-11-28 09:57:49.309608

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID



# revision identifiers, used by Alembic.
revision = 'b6d57334a17e'
down_revision = '905a12a26853'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add CDPS columns and convert existing data.
    
    5-Step Conversion Process:
    1. Service Providers → entity_class='service_provider', all capabilities False
    2. Sellers → entity_class='business_entity', domestic_sell_india=True
    3. Buyers → entity_class='business_entity', domestic_buy_india=True
    4. Traders → entity_class='business_entity', both buy and sell True
    5. Importers/Exporters → import_allowed/export_allowed=True
    6. Foreign Entities → home_country capabilities ONLY (domestic_buy_india=False, domestic_sell_india=False)
    """
    
    # ============================================
    # STEP 1: Add New Columns
    # ============================================
    
    # Entity classification
    op.add_column('business_partners', sa.Column(
        'entity_class',
        sa.String(20),
        nullable=True,  # Nullable during migration
        comment='business_entity (can trade) OR service_provider (cannot trade)'
    ))
    op.create_index('ix_business_partners_entity_class', 'business_partners', ['entity_class'])
    
    # Capabilities (JSONB)
    op.add_column('business_partners', sa.Column(
        'capabilities',
        JSON,
        nullable=True,
        server_default=sa.text("'{}'::json"),
        comment='Auto-detected capabilities from verified documents'
    ))
    
    # Entity hierarchy fields
    op.add_column('business_partners', sa.Column(
        'master_entity_id',
        UUID(as_uuid=True),
        nullable=True,
        comment='If this is a branch/subsidiary, points to master entity'
    ))
    op.create_index('ix_business_partners_master_entity_id', 'business_partners', ['master_entity_id'])
    op.create_foreign_key(
        'fk_business_partners_master_entity_id',
        'business_partners',
        'business_partners',
        ['master_entity_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    op.add_column('business_partners', sa.Column(
        'is_master_entity',
        sa.Boolean,
        nullable=False,
        server_default=sa.text('false'),
        comment='True if this entity has branches/subsidiaries'
    ))
    
    op.add_column('business_partners', sa.Column(
        'corporate_group_id',
        UUID(as_uuid=True),
        nullable=True,
        comment='Entities in same group cannot trade with each other (insider trading prevention)'
    ))
    op.create_index('ix_business_partners_corporate_group_id', 'business_partners', ['corporate_group_id'])
    
    op.add_column('business_partners', sa.Column(
        'entity_hierarchy',
        JSON,
        nullable=True,
        comment='Full entity hierarchy metadata for compliance'
    ))
    
    # ============================================
    # STEP 2: Make old columns nullable
    # ============================================
    op.alter_column('business_partners', 'partner_type', nullable=True)
    
    # ============================================
    # STEP 3: Data Conversion
    # ============================================
    
    # Step 3.1: Service Providers (broker, sub_broker, transporter, controller, financer, shipping_agent)
    # → entity_class='service_provider', all capabilities False
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'service_provider',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', false,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: ' || partner_type,
                'migration_date', NOW()::text
            )
        WHERE partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent')
    """)
    
    # Step 3.2: Sellers (domestic)
    # → entity_class='business_entity', domestic_sell_india=True
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', true,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: seller',
                'migration_date', NOW()::text
            )
        WHERE partner_type = 'seller' 
        AND (trade_classification = 'domestic' OR trade_classification IS NULL)
        AND country = 'India'
    """)
    
    # Step 3.3: Buyers (domestic)
    # → entity_class='business_entity', domestic_buy_india=True
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', true,
                'domestic_sell_india', false,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: buyer',
                'migration_date', NOW()::text
            )
        WHERE partner_type = 'buyer' 
        AND (trade_classification = 'domestic' OR trade_classification IS NULL)
        AND country = 'India'
    """)
    
    # Step 3.4: Traders (both buy and sell)
    # → entity_class='business_entity', both capabilities True
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', true,
                'domestic_sell_india', true,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: trader',
                'migration_date', NOW()::text
            )
        WHERE partner_type = 'trader'
        AND country = 'India'
    """)
    
    # Step 3.5: Importers (foreign buying from India)
    # → entity_class='business_entity', import_allowed=True
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', false,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', true,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: importer (foreign buying from India)',
                'migration_date', NOW()::text
            )
        WHERE partner_type = 'importer'
        OR trade_classification = 'importer'
    """)
    
    # Step 3.6: Exporters (foreign selling to India)
    # → entity_class='business_entity', export_allowed=True
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', false,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', true,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated from partner_type: exporter (foreign selling to India)',
                'migration_date', NOW()::text
            )
        WHERE partner_type = 'exporter'
        OR trade_classification = 'exporter'
    """)
    
    # Step 3.7: ⚠️ CRITICAL - Foreign Entities (domestic trade in THEIR home country ONLY)
    # Foreign sellers/buyers/traders → home_country capabilities, NOT India capabilities
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', false,
                'domestic_buy_home_country', CASE 
                    WHEN partner_type IN ('buyer', 'trader') THEN true 
                    ELSE false 
                END,
                'domestic_sell_home_country', CASE 
                    WHEN partner_type IN ('seller', 'trader') THEN true 
                    ELSE false 
                END,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Migrated foreign entity: can trade ONLY in ' || country || ' (NOT India)',
                'migration_date', NOW()::text
            )
        WHERE country != 'India'
        AND partner_type IN ('seller', 'buyer', 'trader')
        AND (trade_classification = 'domestic' OR trade_classification IS NULL)
    """)
    
    # Step 3.8: Handle any remaining unmigrated records
    op.execute("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            capabilities = jsonb_build_object(
                'domestic_buy_india', false,
                'domestic_sell_india', false,
                'domestic_buy_home_country', false,
                'domestic_sell_home_country', false,
                'import_allowed', false,
                'export_allowed', false,
                'auto_detected', false,
                'detected_from_documents', '[]'::jsonb,
                'detected_at', null,
                'manual_override', false,
                'override_reason', 'Unmigrated - needs manual review',
                'migration_date', NOW()::text
            )
        WHERE entity_class IS NULL
    """)
    
    # ============================================
    # STEP 4: Make entity_class NOT NULL
    # ============================================
    op.alter_column('business_partners', 'entity_class', nullable=False)
    
    # ============================================
    # STEP 5: Create JSONB indexes for performance
    # ============================================
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_domestic_buy_india ON business_partners ((capabilities->>'domestic_buy_india'))
        WHERE (capabilities->>'domestic_buy_india')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_domestic_sell_india ON business_partners ((capabilities->>'domestic_sell_india'))
        WHERE (capabilities->>'domestic_sell_india')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_import_allowed ON business_partners ((capabilities->>'import_allowed'))
        WHERE (capabilities->>'import_allowed')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_export_allowed ON business_partners ((capabilities->>'export_allowed'))
        WHERE (capabilities->>'export_allowed')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_domestic_buy_home ON business_partners ((capabilities->>'domestic_buy_home_country'))
        WHERE (capabilities->>'domestic_buy_home_country')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_domestic_sell_home ON business_partners ((capabilities->>'domestic_sell_home_country'))
        WHERE (capabilities->>'domestic_sell_home_country')::boolean = true
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_capabilities_auto_detected ON business_partners ((capabilities->>'auto_detected'))
        WHERE (capabilities->>'auto_detected')::boolean = true
    """)


def downgrade() -> None:
    """
    Rollback CDPS changes.
    
    WARNING: This will lose capability detection metadata.
    partner_type will be restored from capabilities if possible.
    """
    
    # Drop JSONB indexes
    op.execute("DROP INDEX IF EXISTS idx_capabilities_domestic_buy_india")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_domestic_sell_india")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_import_allowed")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_export_allowed")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_domestic_buy_home")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_domestic_sell_home")
    op.execute("DROP INDEX IF EXISTS idx_capabilities_auto_detected")
    
    # Restore partner_type from entity_class + capabilities (best effort)
    op.execute("""
        UPDATE business_partners
        SET partner_type = CASE
            WHEN entity_class = 'service_provider' THEN service_provider_type
            WHEN (capabilities->>'domestic_buy_india')::boolean = true 
                AND (capabilities->>'domestic_sell_india')::boolean = true THEN 'trader'
            WHEN (capabilities->>'domestic_sell_india')::boolean = true THEN 'seller'
            WHEN (capabilities->>'domestic_buy_india')::boolean = true THEN 'buyer'
            WHEN (capabilities->>'import_allowed')::boolean = true THEN 'importer'
            WHEN (capabilities->>'export_allowed')::boolean = true THEN 'exporter'
            ELSE 'buyer'  -- default fallback
        END
        WHERE partner_type IS NULL
    """)
    
    # Make partner_type NOT NULL again
    op.alter_column('business_partners', 'partner_type', nullable=False)
    
    # Drop new columns
    op.drop_constraint('fk_business_partners_master_entity_id', 'business_partners', type_='foreignkey')
    op.execute('DROP INDEX IF EXISTS ix_business_partners_master_entity_id')
op.drop_column('business_partners', 'master_entity_id')
    
    op.execute('DROP INDEX IF EXISTS ix_business_partners_corporate_group_id')
op.drop_column('business_partners', 'corporate_group_id')
    
    op.drop_column('business_partners', 'entity_hierarchy')
    op.drop_column('business_partners', 'is_master_entity')
    op.drop_column('business_partners', 'capabilities')
    
    op.execute('DROP INDEX IF EXISTS ix_business_partners_entity_class')
op.drop_column('business_partners', 'entity_class')

