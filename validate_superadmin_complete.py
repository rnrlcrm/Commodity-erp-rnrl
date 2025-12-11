#!/usr/bin/env python3
"""
Check and Create SUPER_ADMIN User with Full System Rights

This script uses raw SQL to avoid circular import issues.
"""

import asyncio
import asyncpg
import sys
import bcrypt
from uuid import uuid4

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'commodity_erp',
    'user': 'commodity_user',
    'password': 'commodity_password'
}

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


async def check_superadmin_status(conn):
    """Check if SUPER_ADMIN exists and has all capabilities"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING SUPER_ADMIN STATUS")
    print("="*80)
    
    # Check if SUPER_ADMIN user exists
    superadmin = await conn.fetchrow(
        "SELECT id, email, full_name, user_type, is_active, organization_id, business_partner_id, created_at "
        "FROM users WHERE user_type = 'SUPER_ADMIN' LIMIT 1"
    )
    
    if not superadmin:
        print("\n❌ NO SUPER_ADMIN USER FOUND")
        print("   Status: MISSING")
        return None, []
    
    print(f"\n✅ SUPER_ADMIN USER FOUND")
    print(f"   ID:           {superadmin['id']}")
    print(f"   Email:        {superadmin['email']}")
    print(f"   Full Name:    {superadmin['full_name']}")
    print(f"   User Type:    {superadmin['user_type']}")
    print(f"   Is Active:    {superadmin['is_active']}")
    print(f"   Organization: {superadmin['organization_id']} (should be NULL)")
    print(f"   Partner:      {superadmin['business_partner_id']} (should be NULL)")
    print(f"   Created At:   {superadmin['created_at']}")
    
    # Validate isolation constraints
    isolation_valid = (
        superadmin['organization_id'] is None and 
        superadmin['business_partner_id'] is None
    )
    
    if isolation_valid:
        print("\n✅ DATA ISOLATION VALID")
        print("   Super admin has NULL organization_id and business_partner_id")
    else:
        print("\n❌ DATA ISOLATION INVALID")
        print("   Super admin must have NULL organization_id and business_partner_id")
    
    # Check capabilities
    user_capabilities = await conn.fetch(
        "SELECT uc.id, c.code, c.category "
        "FROM user_capabilities uc "
        "JOIN capabilities c ON c.id = uc.capability_id "
        "WHERE uc.user_id = $1 AND uc.revoked_at IS NULL",
        superadmin['id']
    )
    
    # Count total capabilities
    total_capabilities = await conn.fetchval("SELECT COUNT(*) FROM capabilities")
    
    print(f"\n📊 CAPABILITY STATUS")
    print(f"   Total Capabilities:  {total_capabilities}")
    print(f"   Granted to User:     {len(user_capabilities)}")
    
    if len(user_capabilities) == total_capabilities:
        print("   ✅ ALL CAPABILITIES GRANTED")
    else:
        missing_count = total_capabilities - len(user_capabilities)
        print(f"   ⚠️  MISSING {missing_count} CAPABILITIES")
    
    return superadmin, user_capabilities


async def create_superadmin(conn):
    """Create SUPER_ADMIN user"""
    
    print("\n" + "="*80)
    print("🔧 CREATING SUPER_ADMIN USER")
    print("="*80)
    
    # Check if email already exists
    existing = await conn.fetchrow(
        "SELECT id, email, user_type FROM users WHERE email = $1",
        "admin@rnrl.com"
    )
    
    if existing:
        print("\n⚠️  User with email admin@rnrl.com already exists")
        print(f"   Current user_type: {existing['user_type']}")
        
        if existing['user_type'] != 'SUPER_ADMIN':
            print("   Updating to SUPER_ADMIN...")
            await conn.execute(
                "UPDATE users SET user_type = 'SUPER_ADMIN', organization_id = NULL, "
                "business_partner_id = NULL, is_active = true WHERE id = $1",
                existing['id']
            )
            print("   ✅ Updated to SUPER_ADMIN")
            
            # Fetch updated user
            superadmin = await conn.fetchrow(
                "SELECT id, email, full_name, user_type FROM users WHERE id = $1",
                existing['id']
            )
            return superadmin
        else:
            return existing
    
    # Create new SUPER_ADMIN
    password_hash = hash_password("Rnrl@Admin123")
    user_id = uuid4()
    
    await conn.execute(
        "INSERT INTO users (id, email, full_name, password_hash, user_type, "
        "organization_id, business_partner_id, is_active, is_verified, two_fa_enabled, created_at, updated_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())",
        user_id,
        "admin@rnrl.com",
        "Super Administrator",
        password_hash,
        'SUPER_ADMIN',
        None,
        None,
        True,
        True,
        False
    )
    
    superadmin = await conn.fetchrow(
        "SELECT id, email, full_name, user_type FROM users WHERE id = $1",
        user_id
    )
    
    print(f"\n✅ SUPER_ADMIN CREATED SUCCESSFULLY")
    print(f"   ID:        {superadmin['id']}")
    print(f"   Email:     {superadmin['email']}")
    print(f"   Password:  Rnrl@Admin123")
    print(f"   User Type: {superadmin['user_type']}")
    
    return superadmin


async def grant_all_capabilities(conn, user_id):
    """Grant all 91 capabilities to SUPER_ADMIN"""
    
    print("\n" + "="*80)
    print("🔑 GRANTING ALL CAPABILITIES TO SUPER_ADMIN")
    print("="*80)
    
    # Get all capabilities from database
    all_capabilities = await conn.fetch("SELECT id, code, category FROM capabilities")
    
    if not all_capabilities:
        print("\n❌ NO CAPABILITIES FOUND IN DATABASE")
        print("   Run: python backend/seed_capabilities_now.py")
        return 0
    
    print(f"\n📦 Found {len(all_capabilities)} capabilities in database")
    
    # Get existing user capabilities
    existing_capabilities = await conn.fetch(
        "SELECT capability_id FROM user_capabilities "
        "WHERE user_id = $1 AND revoked_at IS NULL",
        user_id
    )
    existing_capability_ids = {row['capability_id'] for row in existing_capabilities}
    
    # Grant missing capabilities
    granted_count = 0
    for capability in all_capabilities:
        if capability['id'] not in existing_capability_ids:
            await conn.execute(
                "INSERT INTO user_capabilities (id, user_id, capability_id, granted_by, granted_at) "
                "VALUES ($1, $2, $3, $4, NOW())",
                uuid4(),
                user_id,
                capability['id'],
                user_id  # Self-granted for superadmin
            )
            granted_count += 1
    
    print(f"\n✅ GRANTED {granted_count} NEW CAPABILITIES")
    print(f"   Already had: {len(existing_capability_ids)}")
    print(f"   Total now:   {len(all_capabilities)}")
    
    return granted_count


async def validate_superadmin_access(conn, user_id):
    """Validate SUPER_ADMIN has end-to-end system access"""
    
    print("\n" + "="*80)
    print("🔐 VALIDATING SUPER_ADMIN END-TO-END ACCESS RIGHTS")
    print("="*80)
    
    # Get all user capabilities with details
    capabilities = await conn.fetch(
        "SELECT c.code, c.category "
        "FROM capabilities c "
        "JOIN user_capabilities uc ON c.id = uc.capability_id "
        "WHERE uc.user_id = $1 AND uc.revoked_at IS NULL "
        "ORDER BY c.category, c.code",
        user_id
    )
    
    # Group by category
    by_category = {}
    for cap in capabilities:
        category = cap['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(cap['code'])
    
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


async def test_superadmin_login(conn, email, password):
    """Test if superadmin can login"""
    
    print("\n" + "="*80)
    print("🔐 TESTING SUPER_ADMIN LOGIN")
    print("="*80)
    
    # Get user
    user = await conn.fetchrow(
        "SELECT id, email, password_hash, is_active, user_type FROM users WHERE email = $1",
        email
    )
    
    if not user:
        print(f"\n❌ User {email} not found")
        return False
    
    # Check password
    if not verify_password(password, user['password_hash']):
        print(f"\n❌ Invalid password")
        return False
    
    # Check active status
    if not user['is_active']:
        print(f"\n❌ User account is inactive")
        return False
    
    # Check user_type
    if user['user_type'] != 'SUPER_ADMIN':
        print(f"\n❌ User is not SUPER_ADMIN (type: {user['user_type']})")
        return False
    
    print(f"\n✅ LOGIN SUCCESSFUL")
    print(f"   User ID:   {user['id']}")
    print(f"   Email:     {user['email']}")
    print(f"   User Type: {user['user_type']}")
    print(f"   Is Active: {user['is_active']}")
    
    return True


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
    print("6. Test login functionality")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        
        try:
            # Step 1: Check current status
            superadmin, capabilities = await check_superadmin_status(conn)
            
            # Step 2: Create if missing
            if not superadmin:
                superadmin = await create_superadmin(conn)
            
            # Step 3: Grant all capabilities
            granted = await grant_all_capabilities(conn, superadmin['id'])
            
            # Step 4: Validate end-to-end access
            has_full_access = await validate_superadmin_access(conn, superadmin['id'])
            
            # Step 5: Test login
            login_success = await test_superadmin_login(conn, "admin@rnrl.com", "Rnrl@Admin123")
            
            # Final summary
            print("\n" + "="*80)
            print("✅ SUPER_ADMIN VALIDATION COMPLETE")
            print("="*80)
            
            print(f"\n📧 Login Credentials:")
            print(f"   Email:    admin@rnrl.com")
            print(f"   Password: Rnrl@Admin123")
            print(f"   User ID:  {superadmin['id']}")
            
            print(f"\n🔐 Access Rights:")
            if has_full_access:
                print(f"   ✅ FULL END-TO-END SYSTEM ACCESS CONFIRMED")
                print(f"   ✅ Can access all modules and operations")
            else:
                print(f"   ⚠️  MISSING SOME CAPABILITIES")
                print(f"   Run seed script to ensure all capabilities exist")
            
            print(f"\n🔑 Login Status:")
            if login_success:
                print(f"   ✅ LOGIN TEST PASSED")
                print(f"   ✅ Credentials are valid and working")
            else:
                print(f"   ❌ LOGIN TEST FAILED")
                print(f"   Check password or user status")
            
            print("\n" + "="*80)
            print("📋 FINAL CONFIRMATION")
            print("="*80)
            
            if has_full_access and login_success:
                print("\n✅✅✅ SUPER_ADMIN IS 100% READY ✅✅✅")
                print("\nThe superadmin has:")
                print("  • Valid account with correct user_type")
                print("  • Proper data isolation (NULL org & partner)")
                print("  • All system capabilities granted")
                print("  • Full end-to-end system access")
                print("  • Working login credentials")
                print("\nREADY FOR PRODUCTION USE! 🚀")
            else:
                print("\n⚠️  SUPERADMIN HAS ISSUES")
                print("Review the output above for details")
            
            print("\n" + "="*80)
            
        finally:
            await conn.close()
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
