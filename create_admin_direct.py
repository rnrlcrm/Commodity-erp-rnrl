import asyncio
import uuid
from datetime import datetime
import os
import asyncpg
from passlib.context import CryptContext

# --- Configuration ---
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@rnrl.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Rnrl@Admin1")
ADMIN_FULL_NAME = os.environ.get("ADMIN_FULL_NAME", "Super Administrator")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_BYTES = 72  # bcrypt limit

def hash_password(password: str) -> str:
    """Truncate and hash password safely for bcrypt."""
    truncated = password.encode("utf-8")[:MAX_BCRYPT_BYTES]
    truncated_str = truncated.decode("utf-8", errors="ignore")
    return pwd_context.hash(truncated_str)

def default_for_column(column_type: str):
    """Return a sensible default value based on column type."""
    if column_type.startswith("boolean"):
        return False
    elif column_type.startswith("uuid"):
        return None
    elif column_type.startswith("timestamp"):
        return datetime.utcnow()
    elif column_type.startswith("varchar"):
        return ""
    elif column_type.startswith("int") or column_type.startswith("numeric"):
        return 0
    else:
        return None

async def get_not_null_columns(conn, table_name: str):
    """Return a dict of NOT NULL columns and their data types for a table."""
    rows = await conn.fetch(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name=$1 AND is_nullable='NO'
        """,
        table_name
    )
    return {row["column_name"]: row["data_type"] for row in rows}

async def create_admin_user():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Check if admin already exists
        existing = await conn.fetchrow("SELECT * FROM users WHERE email=$1", ADMIN_EMAIL)
        if existing:
            print(f"✅ Admin user '{ADMIN_EMAIL}' already exists. Skipping creation.")
            return

        user_id = str(uuid.uuid4())
        hashed_password = hash_password(ADMIN_PASSWORD)

        # Known SUPER_ADMIN NOT NULL columns
        admin_data = {
            "id": user_id,
            "user_type": "SUPER_ADMIN",
            "organization_id": None,
            "business_partner_id": None,
            "is_active": True,
            "two_fa_enabled": False,
            "is_verified": True,
            "email": ADMIN_EMAIL,
            "password_hash": hashed_password,
            "full_name": ADMIN_FULL_NAME,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Auto-detect other NOT NULL columns not yet in admin_data
        not_null_cols = await get_not_null_columns(conn, "users")
        for col, col_type in not_null_cols.items():
            if col not in admin_data:
                admin_data[col] = default_for_column(col_type)

        # Build insert dynamically
        columns = ", ".join(admin_data.keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(admin_data)))
        values = list(admin_data.values())

        await conn.execute(
            f"INSERT INTO users ({columns}) VALUES ({placeholders})",
            *values
        )
        print(f"✅ SUPER_ADMIN user '{ADMIN_EMAIL}' created successfully with all NOT NULL columns handled.")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
