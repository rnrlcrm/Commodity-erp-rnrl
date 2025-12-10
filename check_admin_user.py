import asyncio
import asyncpg
from passlib.context import CryptContext

DB_HOST = "10.40.0.3"
DB_PORT = 5432
DB_USER = "commodity_user"
DB_PASSWORD = "6soz/ALiY0+uaf9te/iZ6CewozSaBYQCJlmNKVnvLDc="
DB_NAME = "commodity_erp"

ADMIN_EMAIL = "admin@rnrl.com"
ADMIN_PASSWORD = "Rnrl@Admin1"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_user():
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        user = await conn.fetchrow(
            """
            SELECT id, email, user_type, is_active, two_fa_enabled, 
                   is_verified, password_hash, organization_id, business_partner_id
            FROM users 
            WHERE email = $1
            """,
            ADMIN_EMAIL
        )
        
        if not user:
            print(f"❌ User '{ADMIN_EMAIL}' NOT FOUND in database!")
            return
        
        print(f"✅ User found:")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   User Type: {user['user_type']}")
        print(f"   Is Active: {user['is_active']}")
        print(f"   2FA Enabled: {user['two_fa_enabled']}")
        print(f"   Is Verified: {user['is_verified']}")
        print(f"   Organization ID: {user['organization_id']}")
        print(f"   Business Partner ID: {user['business_partner_id']}")
        print(f"   Password Hash: {user['password_hash'][:50]}...")
        
        # Test password verification
        print(f"\n🔐 Testing password verification...")
        if pwd_context.verify(ADMIN_PASSWORD, user['password_hash']):
            print(f"   ✅ Password '{ADMIN_PASSWORD}' MATCHES!")
        else:
            print(f"   ❌ Password '{ADMIN_PASSWORD}' DOES NOT MATCH!")
            print(f"   💡 Creating correct hash for reference:")
            correct_hash = pwd_context.hash(ADMIN_PASSWORD)
            print(f"   New hash: {correct_hash}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_user())
