#!/usr/bin/env python3
"""
Direct Super Admin User Creator for PostgreSQL
- Works in Cloud Run
- Uses asyncpg and passlib for secure password hashing
- Matches the current SUPER_ADMIN schema exactly
"""

import asyncio
import asyncpg
from passlib.context import CryptContext
from uuid import uuid4

# --------------------------
# Password hashing
# --------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------
# Configuration
# --------------------------
DB_HOST = "10.40.0.3"
DB_PORT = 5432
DB_USER = "commodity_user"
DB_PASSWORD = "6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc="
DB_NAME = "commodity_erp"

ADMIN_EMAIL = "admin@rnrl.com"
ADMIN_PASSWORD = "Rnrl@Admin1"  # Must follow your password policy
ADMIN_FULL_NAME = "Super Administrator"

# --------------------------
# Main function
# --------------------------
async def create_admin_user():
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    try:
        # Check if admin already exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            ADMIN_EMAIL
        )
        if existing:
            print(f"✅ Admin already exists! User ID: {existing['id']}")
            return

        # Hash the password
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        user_id = uuid4()

        # Insert super admin user
        await conn.execute("""
            INSERT INTO users (
                id, email, password_hash, full_name,
                is_active, user_type,
                organization_id, business_partner_id,
                two_fa_enabled,
                created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4,
                true, 'SUPER_ADMIN',
                NULL, NULL,
                false,
                NOW(), NOW()
            )
        """,
            user_id, ADMIN_EMAIL, hashed_password, ADMIN_FULL_NAME
        )

        print("✅ Super Admin created successfully!")
        print(f"User ID: {user_id}")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")

    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
