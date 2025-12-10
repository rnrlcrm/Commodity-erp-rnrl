#!/usr/bin/env python3
"""
Simple Super Admin Creator - Tested and Working
Connects directly to Cloud SQL and creates admin user
"""
import asyncio
import asyncpg
from passlib.context import CryptContext
from uuid import uuid4
from datetime import datetime

# Database connection
DB_HOST = "10.40.0.3"
DB_PORT = 5432
DB_USER = "commodity_user"
DB_PASSWORD = "6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc="
DB_NAME = "commodity_erp"

# Admin credentials
ADMIN_EMAIL = "admin@rnrl.com"
ADMIN_PASSWORD = "Rnrl@Admin1"
ADMIN_NAME = "Super Administrator"

# Use pbkdf2_sha256 (matches backend exactly)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

async def main():
    print("Connecting to database...")
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        # Delete existing admin if exists
        print(f"Checking for existing user: {ADMIN_EMAIL}")
        await conn.execute("DELETE FROM users WHERE email = $1", ADMIN_EMAIL)
        print("Deleted any existing admin user")
        
        # Hash password
        print("Hashing password...")
        password_hash = pwd_context.hash(ADMIN_PASSWORD)
        
        # Create new admin
        user_id = uuid4()
        now = datetime.utcnow()
        
        print("Creating super admin user...")
        await conn.execute("""
            INSERT INTO users (
                id, email, password_hash, full_name,
                user_type, is_active, two_fa_enabled, is_verified,
                organization_id, business_partner_id,
                created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4,
                'SUPER_ADMIN', true, false, true,
                NULL, NULL,
                $5, $6
            )
        """, user_id, ADMIN_EMAIL, password_hash, ADMIN_NAME, now, now)
        
        print("\n✅ SUCCESS!")
        print(f"User ID: {user_id}")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"\nLogin at: https://frontend-service-565186585906.us-central1.run.app/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
