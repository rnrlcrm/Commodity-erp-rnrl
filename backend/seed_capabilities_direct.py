"""
Direct capability seeding script that doesn't import backend modules
"""
import asyncio
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from enum import Enum

DATABASE_URL = "postgresql+asyncpg://commodity_user:commodity_password@localhost:5432/commodity_erp"


class Capabilities(str, Enum):
    """All capabilities - copied from definitions.py"""
    # AUTH
    AUTH_LOGIN = "AUTH_LOGIN"
    AUTH_REGISTER = "AUTH_REGISTER"
    AUTH_RESET_PASSWORD = "AUTH_RESET_PASSWORD"
    AUTH_VERIFY_EMAIL = "AUTH_VERIFY_EMAIL"
    AUTH_MANAGE_SESSIONS = "AUTH_MANAGE_SESSIONS"
    AUTH_CREATE_ACCOUNT = "AUTH_CREATE_ACCOUNT"
    AUTH_UPDATE_PROFILE = "AUTH_UPDATE_PROFILE"
    PUBLIC_ACCESS = "PUBLIC_ACCESS"
    
    # ORGANIZATION
    ORG_CREATE = "ORG_CREATE"
    ORG_READ = "ORG_READ"
    ORG_UPDATE = "ORG_UPDATE"
    ORG_DELETE = "ORG_DELETE"
    ORG_MANAGE_USERS = "ORG_MANAGE_USERS"
    ORG_MANAGE_ROLES = "ORG_MANAGE_ROLES"
    ORG_VIEW_AUDIT_LOGS = "ORG_VIEW_AUDIT_LOGS"
    
    # PARTNER
    PARTNER_CREATE = "PARTNER_CREATE"
    PARTNER_READ = "PARTNER_READ"
    PARTNER_UPDATE = "PARTNER_UPDATE"
    PARTNER_DELETE = "PARTNER_DELETE"
    PARTNER_APPROVE = "PARTNER_APPROVE"
    PARTNER_VERIFY_GST = "PARTNER_VERIFY_GST"
    PARTNER_MANAGE_BANK_ACCOUNTS = "PARTNER_MANAGE_BANK_ACCOUNTS"
    PARTNER_VIEW_SENSITIVE = "PARTNER_VIEW_SENSITIVE"
    
    # COMMODITY
    COMMODITY_CREATE = "COMMODITY_CREATE"
    COMMODITY_READ = "COMMODITY_READ"
    COMMODITY_UPDATE = "COMMODITY_UPDATE"
    COMMODITY_DELETE = "COMMODITY_DELETE"
    COMMODITY_UPDATE_PRICE = "COMMODITY_UPDATE_PRICE"
    COMMODITY_MANAGE_SPECIFICATIONS = "COMMODITY_MANAGE_SPECIFICATIONS"
    COMMODITY_MANAGE_HSN = "COMMODITY_MANAGE_HSN"
    
    # LOCATION
    LOCATION_CREATE = "LOCATION_CREATE"
    LOCATION_READ = "LOCATION_READ"
    LOCATION_UPDATE = "LOCATION_UPDATE"
    LOCATION_DELETE = "LOCATION_DELETE"
    LOCATION_MANAGE_HIERARCHY = "LOCATION_MANAGE_HIERARCHY"
    
    # AVAILABILITY
    AVAILABILITY_CREATE = "AVAILABILITY_CREATE"
    AVAILABILITY_READ = "AVAILABILITY_READ"
    AVAILABILITY_UPDATE = "AVAILABILITY_UPDATE"
    AVAILABILITY_DELETE = "AVAILABILITY_DELETE"
    AVAILABILITY_APPROVE = "AVAILABILITY_APPROVE"
    AVAILABILITY_REJECT = "AVAILABILITY_REJECT"
    AVAILABILITY_RESERVE = "AVAILABILITY_RESERVE"
    AVAILABILITY_RELEASE = "AVAILABILITY_RELEASE"
    AVAILABILITY_MARK_SOLD = "AVAILABILITY_MARK_SOLD"
    AVAILABILITY_CANCEL = "AVAILABILITY_CANCEL"
    AVAILABILITY_VIEW_ANALYTICS = "AVAILABILITY_VIEW_ANALYTICS"
    
    # REQUIREMENT
    REQUIREMENT_CREATE = "REQUIREMENT_CREATE"
    REQUIREMENT_READ = "REQUIREMENT_READ"
    REQUIREMENT_UPDATE = "REQUIREMENT_UPDATE"
    REQUIREMENT_DELETE = "REQUIREMENT_DELETE"
    REQUIREMENT_APPROVE = "REQUIREMENT_APPROVE"
    REQUIREMENT_REJECT = "REQUIREMENT_REJECT"
    REQUIREMENT_AI_ADJUST = "REQUIREMENT_AI_ADJUST"
    REQUIREMENT_CANCEL = "REQUIREMENT_CANCEL"
    REQUIREMENT_FULFILL = "REQUIREMENT_FULFILL"
    REQUIREMENT_VIEW_ANALYTICS = "REQUIREMENT_VIEW_ANALYTICS"
    
    # MATCHING
    MATCHING_EXECUTE = "MATCHING_EXECUTE"
    MATCHING_VIEW_RESULTS = "MATCHING_VIEW_RESULTS"
    MATCHING_APPROVE_MATCH = "MATCHING_APPROVE_MATCH"
    MATCHING_REJECT_MATCH = "MATCHING_REJECT_MATCH"
    MATCHING_CONFIGURE_RULES = "MATCHING_CONFIGURE_RULES"
    MATCHING_MANUAL = "MATCHING_MANUAL"
    
    # SETTINGS
    SETTINGS_VIEW_ALL = "SETTINGS_VIEW_ALL"
    SETTINGS_MANAGE_ORGANIZATIONS = "SETTINGS_MANAGE_ORGANIZATIONS"
    SETTINGS_MANAGE_COMMODITIES = "SETTINGS_MANAGE_COMMODITIES"
    SETTINGS_MANAGE_LOCATIONS = "SETTINGS_MANAGE_LOCATIONS"
    
    # INVOICE
    INVOICE_CREATE_ANY_BRANCH = "INVOICE_CREATE_ANY_BRANCH"
    INVOICE_VIEW_ALL_BRANCHES = "INVOICE_VIEW_ALL_BRANCHES"
    INVOICE_VIEW_OWN = "INVOICE_VIEW_OWN"
    
    # CONTRACT
    CONTRACT_VIEW_OWN = "CONTRACT_VIEW_OWN"
    
    # PAYMENT
    PAYMENT_VIEW_OWN = "PAYMENT_VIEW_OWN"
    
    # SHIPMENT
    SHIPMENT_VIEW_OWN = "SHIPMENT_VIEW_OWN"
    
    # DATA PRIVACY
    DATA_EXPORT_OWN = "DATA_EXPORT_OWN"
    DATA_DELETE_OWN = "DATA_DELETE_OWN"
    DATA_EXPORT_ALL = "DATA_EXPORT_ALL"
    DATA_DELETE_ALL = "DATA_DELETE_ALL"
    
    # AUDIT
    AUDIT_VIEW_ALL = "AUDIT_VIEW_ALL"
    AUDIT_EXPORT = "AUDIT_EXPORT"
    
    # ADMIN
    ADMIN_MANAGE_USERS = "ADMIN_MANAGE_USERS"
    ADMIN_MANAGE_ROLES = "ADMIN_MANAGE_ROLES"
    ADMIN_MANAGE_CAPABILITIES = "ADMIN_MANAGE_CAPABILITIES"
    ADMIN_VIEW_ALL_DATA = "ADMIN_VIEW_ALL_DATA"
    ADMIN_EXECUTE_MIGRATIONS = "ADMIN_EXECUTE_MIGRATIONS"
    ADMIN_VIEW_SYSTEM_LOGS = "ADMIN_VIEW_SYSTEM_LOGS"
    ADMIN_MANAGE_INTEGRATIONS = "ADMIN_MANAGE_INTEGRATIONS"
    
    # SYSTEM
    SYSTEM_API_ACCESS = "SYSTEM_API_ACCESS"
    SYSTEM_WEBSOCKET_ACCESS = "SYSTEM_WEBSOCKET_ACCESS"
    SYSTEM_EXPORT_DATA = "SYSTEM_EXPORT_DATA"
    SYSTEM_IMPORT_DATA = "SYSTEM_IMPORT_DATA"
    SYSTEM_VIEW_AUDIT_TRAIL = "SYSTEM_VIEW_AUDIT_TRAIL"
    SYSTEM_CONFIGURE = "SYSTEM_CONFIGURE"


async def seed_capabilities():
    """Seed all capabilities into database"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    capabilities_data = []
    for capability in Capabilities:
        category = capability.value.split("_")[0].lower()
        capabilities_data.append({
            "id": str(uuid.uuid4()),
            "code": capability.value,
            "name": capability.value.replace("_", " ").title(),
            "description": f"Capability: {capability.value}",
            "category": category,
            "is_system": category in ["auth", "system", "admin"],
        })
    
    print(f"\n🌱 Seeding {len(capabilities_data)} capabilities...")
    
    async with engine.begin() as conn:
        # Check if already seeded
        result = await conn.execute(text("SELECT COUNT(*) FROM capabilities"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing capabilities. Clearing...")
            await conn.execute(text("DELETE FROM capabilities"))
        
        # Bulk insert
        for cap in capabilities_data:
            await conn.execute(
                text("""
                    INSERT INTO capabilities (id, code, name, description, category, is_system, created_at, updated_at)
                    VALUES (:id, :code, :name, :description, :category, :is_system, NOW(), NOW())
                """),
                cap
            )
        
        print(f"✅ Successfully seeded {len(capabilities_data)} capabilities!")
        
        # Show breakdown by category
        result = await conn.execute(text("""
            SELECT category, COUNT(*) as count 
            FROM capabilities 
            GROUP BY category 
            ORDER BY category
        """))
        
        print("\n📊 Capabilities by category:")
        for row in result:
            print(f"   {row.category}: {row.count}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_capabilities())
