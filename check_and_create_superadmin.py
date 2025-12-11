#!/usr/bin/env python3
"""
Check and Create SUPER_ADMIN User with Full System Rights

This script:
1. Checks if SUPER_ADMIN user exists
2. Validates SUPER_ADMIN has all 91 capabilities
3. Creates SUPER_ADMIN if missing
4. Grants all capabilities if missing
5. Validates end-to-end system access rights
"""

import asyncio
import sys
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Database connection
DATABASE_URL = "postgresql+asyncpg://commodity_user:commodity_password@localhost:5432/commodity_erp"

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def check_superadmin_status(db: AsyncSession):
    """Check if SUPER_ADMIN exists and has all capabilities"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING SUPER_ADMIN STATUS")
    print("="*80)
    
    # Check if SUPER_ADMIN user exists using raw SQL
    result = await db.execute(
        text("SELECT id, email, full_name, user_type, is_active, organization_id, business_partner_id, created_at FROM users WHERE user_type = 'SUPER_ADMIN' LIMIT 1")
    )
    row = result.first()
    
    if not superadmin:
        print("\n❌ NO SUPER_ADMIN USER FOUND")
        print("   Status: MISSING")
        return None, []
    
    print(f"\n✅ SUPER_ADMIN USER FOUND")
    print(f"   ID:           {superadmin.id}")
    print(f"   Email:        {superadmin.email}")
    print(f"   Full Name:    {superadmin.full_name}")
    print(f"   User Type:    {superadmin.user_type}")
    print(f"   Is Active:    {superadmin.is_active}")
    print(f"   Organization: {superadmin.organization_id} (should be NULL)")
    print(f"   Partner:      {superadmin.business_partner_id} (should be NULL)")
    print(f"   Created At:   {superadmin.created_at}")
    
    # Validate isolation constraints
    isolation_valid = (
        superadmin.organization_id is None and 
        superadmin.business_partner_id is None
    )
    
    if isolation_valid:
        print("\n✅ DATA ISOLATION VALID")
        print("   Super admin has NULL organization_id and business_partner_id")
    else:
        print("\n❌ DATA ISOLATION INVALID")
        print("   Super admin must have NULL organization_id and business_partner_id")
    
    # Check capabilities
    result = await db.execute(
        select(UserCapability)
        .where(UserCapability.user_id == superadmin.id)
        .where(UserCapability.revoked_at.is_(None))
    )
    user_capabilities = result.scalars().all()
    
    print(f"\n📊 CAPABILITY STATUS")
    print(f"   Total Capabilities:  {len(list(Capabilities))}")
    print(f"   Granted to User:     {len(user_capabilities)}")
    
    if len(user_capabilities) == len(list(Capabilities)):
        print("   ✅ ALL CAPABILITIES GRANTED")
    else:
        missing_count = len(list(Capabilities)) - len(user_capabilities)
        print(f"   ⚠️  MISSING {missing_count} CAPABILITIES")
    
    return superadmin, user_capabilities


async def create_superadmin(db: AsyncSession):
    """Create SUPER_ADMIN user"""
    
    print("\n" + "="*80)
    print("🔧 CREATING SUPER_ADMIN USER")
    print("="*80)
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == "admin@rnrl.com")
    )
    existing = result.scalars().first()
    
    if existing:
        print("\n⚠️  User with email admin@rnrl.com already exists")
        print(f"   Current user_type: {existing.user_type}")
        
        if existing.user_type != 'SUPER_ADMIN':
            print("   Updating to SUPER_ADMIN...")
            existing.user_type = 'SUPER_ADMIN'
            existing.organization_id = None
            existing.business_partner_id = None
            existing.is_active = True
            await db.commit()
            await db.refresh(existing)
            print("   ✅ Updated to SUPER_ADMIN")
            return existing
        else:
            return existing
    
    # Create new SUPER_ADMIN
    password_hash = pwd_context.hash("Rnrl@Admin123")
    
    superadmin = User(
        email="admin@rnrl.com",
        full_name="Super Administrator",
        password_hash=password_hash,
        user_type='SUPER_ADMIN',
        organization_id=None,
        business_partner_id=None,
        is_active=True,
        is_verified=True
    )
    
    db.add(superadmin)
    await db.commit()
    await db.refresh(superadmin)
    
    print(f"\n✅ SUPER_ADMIN CREATED SUCCESSFULLY")
    print(f"   ID:        {superadmin.id}")
    print(f"   Email:     {superadmin.email}")
    print(f"   Password:  Rnrl@Admin123")
    print(f"   User Type: {superadmin.user_type}")
    
    return superadmin


async def grant_all_capabilities(db: AsyncSession, user_id: UUID):
    """Grant all 91 capabilities to SUPER_ADMIN"""
    
    print("\n" + "="*80)
    print("🔑 GRANTING ALL CAPABILITIES TO SUPER_ADMIN")
    print("="*80)
    
    # Get all capabilities from database
    result = await db.execute(select(Capability))
    all_capabilities = result.scalars().all()
    
    if not all_capabilities:
        print("\n❌ NO CAPABILITIES FOUND IN DATABASE")
        print("   Run: python backend/seed_capabilities_now.py")
        return 0
    
    print(f"\n📦 Found {len(all_capabilities)} capabilities in database")
    
    # Get existing user capabilities
    result = await db.execute(
        select(UserCapability.capability_id)
        .where(UserCapability.user_id == user_id)
        .where(UserCapability.revoked_at.is_(None))
    )
    existing_capability_ids = set(row[0] for row in result.all())
    
    # Grant missing capabilities
    granted_count = 0
    for capability in all_capabilities:
        if capability.id not in existing_capability_ids:
            user_capability = UserCapability(
                user_id=user_id,
                capability_id=capability.id,
                granted_by=user_id  # Self-granted for superadmin
            )
            db.add(user_capability)
            granted_count += 1
    
    await db.commit()
    
    print(f"\n✅ GRANTED {granted_count} NEW CAPABILITIES")
    print(f"   Already had: {len(existing_capability_ids)}")
    print(f"   Total now:   {len(all_capabilities)}")
    
    return granted_count


async def validate_superadmin_access(db: AsyncSession, user_id: UUID):
    """Validate SUPER_ADMIN has end-to-end system access"""
    
    print("\n" + "="*80)
    print("🔐 VALIDATING SUPER_ADMIN END-TO-END ACCESS RIGHTS")
    print("="*80)
    
    # Get all user capabilities with details
    result = await db.execute(
        select(Capability.code, Capability.category)
        .join(UserCapability, Capability.id == UserCapability.capability_id)
        .where(UserCapability.user_id == user_id)
        .where(UserCapability.revoked_at.is_(None))
        .order_by(Capability.category, Capability.code)
    )
    capabilities = result.all()
    
    # Group by category
    by_category = {}
    for code, category in capabilities:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(code)
    
    print(f"\n✅ SUPER_ADMIN HAS ACCESS TO {len(capabilities)} CAPABILITIES")
    print(f"   Across {len(by_category)} Categories\n")
    
    # Critical categories for end-to-end access
    critical_categories = [
        "auth", "org", "partner", "commodity", "location",
        "availability", "requirement", "matching", "settings",
        "invoice", "contract", "payment", "shipment", "admin"
    ]
    
    missing_categories = []
    for category in critical_categories:
        if category in by_category:
            count = len(by_category[category])
            print(f"   ✅ {category.upper():20} - {count} capabilities")
        else:
            print(f"   ❌ {category.upper():20} - MISSING")
            missing_categories.append(category)
    
    # Additional categories
    extra_categories = set(by_category.keys()) - set(critical_categories)
    if extra_categories:
        print(f"\n   Additional Categories:")
        for category in sorted(extra_categories):
            count = len(by_category[category])
            print(f"   ✅ {category.upper():20} - {count} capabilities")
    
    # Summary
    print("\n" + "="*80)
    print("📊 ACCESS RIGHTS SUMMARY")
    print("="*80)
    
    all_critical_present = len(missing_categories) == 0
    
    if all_critical_present:
        print("\n✅ SUPER_ADMIN HAS FULL END-TO-END SYSTEM ACCESS")
        print("   Can access all critical modules:")
        print("   • Authentication & Authorization")
        print("   • Organization Management")
        print("   • Partner Management") 
        print("   • Commodity Trading")
        print("   • Location Management")
        print("   • Availability Management")
        print("   • Requirement Management")
        print("   • Matching Engine")
        print("   • System Settings")
        print("   • Invoice Management")
        print("   • Contract Management")
        print("   • Payment Processing")
        print("   • Shipment Tracking")
        print("   • Admin Operations")
    else:
        print(f"\n⚠️  MISSING ACCESS TO {len(missing_categories)} CRITICAL CATEGORIES")
        for category in missing_categories:
            print(f"   ❌ {category}")
    
    return all_critical_present


async def main():
    """Main execution"""
    
    print("\n" + "="*80)
    print("🚀 SUPER_ADMIN VALIDATION & CREATION SCRIPT")
    print("="*80)
    print("\nThis script will:")
    print("1. Check if SUPER_ADMIN user exists")
    print("2. Validate SUPER_ADMIN has all capabilities")
    print("3. Create SUPER_ADMIN if missing")
    print("4. Grant all capabilities if missing")
    print("5. Validate end-to-end system access rights")
    
    # Create database engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as db:
            # Step 1: Check current status
            superadmin, capabilities = await check_superadmin_status(db)
            
            # Step 2: Create if missing
            if not superadmin:
                superadmin = await create_superadmin(db)
            
            # Step 3: Grant all capabilities
            granted = await grant_all_capabilities(db, superadmin.id)
            
            # Step 4: Validate end-to-end access
            has_full_access = await validate_superadmin_access(db, superadmin.id)
            
            # Final summary
            print("\n" + "="*80)
            print("✅ SUPER_ADMIN VALIDATION COMPLETE")
            print("="*80)
            
            print(f"\n📧 Login Credentials:")
            print(f"   Email:    admin@rnrl.com")
            print(f"   Password: Rnrl@Admin123")
            print(f"   User ID:  {superadmin.id}")
            
            print(f"\n🔐 Access Rights:")
            if has_full_access:
                print(f"   ✅ FULL END-TO-END SYSTEM ACCESS CONFIRMED")
                print(f"   ✅ Can access all modules and operations")
                print(f"   ✅ Has all {len(list(Capabilities))} capabilities")
            else:
                print(f"   ⚠️  MISSING SOME CAPABILITIES")
                print(f"   Run seed script to ensure all capabilities exist")
            
            print("\n" + "="*80)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
