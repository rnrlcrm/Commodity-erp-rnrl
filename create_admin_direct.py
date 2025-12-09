#!/usr/bin/env python3
"""
Direct Database Admin User Creator
Creates admin user directly in PostgreSQL database
FOR USE IN CLOUD RUN JOB WITH VPC CONNECTOR
"""

import asyncio
import asyncpg
from passlib.context import CryptContext
from uuid import uuid4
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create admin user directly in database"""
    
    # Database connection - use separate parameters to avoid special char issues
    conn = await asyncpg.connect(
        host='10.40.0.3',
        port=5432,
        user='commodity_user',
        password='6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc=',
        database='commodity_erp'
    )
    
    try:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1",
            'admin@rnrl.com'
        )
        
        if existing:
            print("✅ Admin user already exists!")
            print("   Email: admin@rnrl.com")
            print(f"   User ID: {existing['id']}")
            print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
            print("   Email:    admin@rnrl.com")
            print("   Password: Rnrl@Admin1")
            return
        
        # Create organization first
        org_id = uuid4()
        await conn.execute("""
            INSERT INTO organizations (id, name, org_type, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT DO NOTHING
        """, org_id, 'RNRL Admin Organization', 'ADMIN')
        
        # Hash password
        hashed_password = pwd_context.hash("Rnrl@Admin1")
        user_id = uuid4()
        
        # Insert superadmin user with SUPER_ADMIN user_type
        await conn.execute("""
            INSERT INTO users (
                id, email, password_hash, full_name,
                is_active, user_type,
                organization_id, business_partner_id,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, true, 'SUPER_ADMIN', NULL, NULL, NOW(), NOW())
        """,
            user_id, 'admin@rnrl.com', hashed_password, 'Super Administrator'
        )
        
        print("✅ Super Admin created successfully!")
        print(f"   User ID: {user_id}")
        print("   Email: admin@rnrl.com")
        print("   Name: Super Administrator")
        print("\n🔐 Login Credentials:")
        print("   Email:    admin@rnrl.com")
        print("   Password: Rnrl@Admin1")
        print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
