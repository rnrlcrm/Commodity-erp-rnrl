import asyncio
import asyncpg
import bcrypt
from uuid import uuid4

async def create_admin_user():
    conn = await asyncpg.connect(
        host='10.40.0.3',
        port=5432,
        user='commodity_user',
        password='6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc=',
        database='commodity_erp'
    )
    try:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            'admin@rnrl.com'
        )
        if existing:
            print(f"✅ Admin already exists! ID: {existing['id']}")
            return

        hashed_password = bcrypt.hashpw("Rnrl@Admin1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = uuid4()

        await conn.execute("""
            INSERT INTO users (
                id, email, password_hash, full_name,
                is_active, user_type,
                organization_id, business_partner_id,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, true, 'SUPER_ADMIN', NULL, NULL, NOW(), NOW())
        """, user_id, 'admin@rnrl.com', hashed_password, 'Super Administrator')

        print("✅ Super Admin created successfully!")
        print(f"User ID: {user_id}")
        print("Email: admin@rnrl.com")
        print("Password: Rnrl@Admin1")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
