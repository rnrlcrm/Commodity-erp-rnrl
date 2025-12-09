#!/usr/bin/env python3
"""
Create Super Admin User - Simple Direct Insert
Run this in Google Cloud Shell with cloud-sql-proxy running
"""

import asyncio
import asyncpg
from uuid import uuid4
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_superadmin():
    """Create superadmin user directly in database"""
    
    # Connect to database via cloud-sql-proxy
    # Make sure cloud-sql-proxy is running with: 
    # cloud-sql-proxy commodity-plafform-sandbox:us-central1:cotton-erp-db --port 5432 &
    
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='commodity_user',
        password='6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc=',
        database='commodity_erp'
    )
    
    try:
        print("🔌 Connected to database")
        
        # Check if admin already exists
        existing = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1",
            'admin@rnrl.com'
        )
        
        if existing:
            print("✅ Super Admin already exists!")
            print("   Email: admin@rnrl.com")
            print(f"   User ID: {existing['id']}")
            print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
            print("   Email:    admin@rnrl.com")
            print("   Password: Admin@123")
            return
        
        # Generate IDs
        user_id = uuid4()
        org_id = uuid4()
        
        # Hash password
        hashed_password = pwd_context.hash("Admin@123")
        
        print("📝 Creating Super Admin...")
        
        # Create organization first
        await conn.execute("""
            INSERT INTO organizations (id, name, org_type, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
        """, org_id, 'RNRL Admin Organization', 'ADMIN')
        
        # Create superadmin user
        await conn.execute("""
            INSERT INTO users (
                id, email, hashed_password, full_name, 
                is_active, is_superuser, organization_id,
                created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, true, true, $5, NOW(), NOW())
        """, user_id, 'admin@rnrl.com', hashed_password, 'Super Administrator', org_id)
        
        print("✅ Super Admin created successfully!")
        print("\n📧 Email:    admin@rnrl.com")
        print("🔑 Password: Admin@123")
        print(f"👤 User ID:  {user_id}")
        print(f"🏢 Org ID:   {org_id}")
        print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("\n🔌 Database connection closed")

if __name__ == '__main__':
    print("=" * 60)
    print("Creating Super Admin User")
    print("=" * 60)
    asyncio.run(create_superadmin())
