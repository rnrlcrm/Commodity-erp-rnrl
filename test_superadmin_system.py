#!/usr/bin/env python3
"""
Comprehensive SUPER_ADMIN System Test
Tests all critical functionality for SUPER_ADMIN validation
"""
import asyncio
import asyncpg
import bcrypt
from datetime import datetime
from typing import Dict, List, Tuple

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'commodity_erp',
    'user': 'commodity_user',
    'password': 'commodity_password'
}

# Expected credentials
EXPECTED_EMAIL = 'admin@rnrl.com'
EXPECTED_PASSWORD = 'Rnrl@Admin1'
EXPECTED_CAPABILITIES = 91

class TestResult:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def pass_test(self, name: str):
        self.passed += 1
        print(f"✅ PASS: {name}")
        
    def fail_test(self, name: str, error: str):
        self.failed += 1
        self.errors.append((name, error))
        print(f"❌ FAIL: {name} - {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")
        
        if self.errors:
            print(f"\n{'='*80}")
            print(f"FAILED TESTS")
            print(f"{'='*80}")
            for name, error in self.errors:
                print(f"\n{name}:")
                print(f"  {error}")
                
        return self.failed == 0


async def test_database_connection(results: TestResult) -> asyncpg.Connection:
    """Test 1: Database connection"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        results.pass_test("Database Connection")
        return conn
    except Exception as e:
        results.fail_test("Database Connection", str(e))
        raise


async def test_superadmin_user_exists(conn: asyncpg.Connection, results: TestResult) -> Dict:
    """Test 2: SUPER_ADMIN user exists"""
    try:
        user = await conn.fetchrow("""
            SELECT id, email, password_hash, user_type, is_active,
                   organization_id, business_partner_id
            FROM users 
            WHERE email = $1 AND user_type = 'SUPER_ADMIN'
        """, EXPECTED_EMAIL)
        
        if not user:
            results.fail_test("SUPER_ADMIN User Exists", "No SUPER_ADMIN user found")
            return None
            
        if user['email'] != EXPECTED_EMAIL:
            results.fail_test("SUPER_ADMIN User Exists", f"Email mismatch: {user['email']}")
            return None
            
        results.pass_test("SUPER_ADMIN User Exists")
        return dict(user)
    except Exception as e:
        results.fail_test("SUPER_ADMIN User Exists", str(e))
        return None


async def test_password_verification(user: Dict, results: TestResult):
    """Test 3: Password verification"""
    try:
        if not user:
            results.fail_test("Password Verification", "No user data")
            return
            
        hashed = user['password_hash'].encode('utf-8')
        password_bytes = EXPECTED_PASSWORD.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, hashed):
            results.pass_test("Password Verification")
        else:
            results.fail_test("Password Verification", "Password does not match")
    except Exception as e:
        results.fail_test("Password Verification", str(e))


async def test_data_isolation(user: Dict, results: TestResult):
    """Test 4: Data isolation (NULL org_id and partner_id)"""
    try:
        if not user:
            results.fail_test("Data Isolation", "No user data")
            return
            
        if user['organization_id'] is not None:
            results.fail_test("Data Isolation", f"organization_id should be NULL but is {user['organization_id']}")
            return
            
        if user['business_partner_id'] is not None:
            results.fail_test("Data Isolation", f"business_partner_id should be NULL but is {user['business_partner_id']}")
            return
            
        results.pass_test("Data Isolation")
    except Exception as e:
        results.fail_test("Data Isolation", str(e))


async def test_user_active(user: Dict, results: TestResult):
    """Test 5: User is active"""
    try:
        if not user:
            results.fail_test("User Active Status", "No user data")
            return
            
        if user['is_active']:
            results.pass_test("User Active Status")
        else:
            results.fail_test("User Active Status", "User is not active")
    except Exception as e:
        results.fail_test("User Active Status", str(e))


async def test_capabilities_seeded(conn: asyncpg.Connection, results: TestResult) -> int:
    """Test 6: All capabilities seeded"""
    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM capabilities")
        
        if count == EXPECTED_CAPABILITIES:
            results.pass_test(f"Capabilities Seeded ({count} capabilities)")
            return count
        else:
            results.fail_test(f"Capabilities Seeded", 
                            f"Expected {EXPECTED_CAPABILITIES}, found {count}")
            return count
    except Exception as e:
        results.fail_test("Capabilities Seeded", str(e))
        return 0


async def test_superadmin_capabilities(conn: asyncpg.Connection, user: Dict, results: TestResult):
    """Test 7: SUPER_ADMIN has all capabilities"""
    try:
        if not user:
            results.fail_test("SUPER_ADMIN Capabilities", "No user data")
            return
            
        count = await conn.fetchval("""
            SELECT COUNT(*) FROM user_capabilities 
            WHERE user_id = $1
        """, user['id'])
        
        if count == EXPECTED_CAPABILITIES:
            results.pass_test(f"SUPER_ADMIN Capabilities ({count}/{EXPECTED_CAPABILITIES})")
        else:
            results.fail_test("SUPER_ADMIN Capabilities",
                            f"Expected {EXPECTED_CAPABILITIES}, found {count}")
    except Exception as e:
        results.fail_test("SUPER_ADMIN Capabilities", str(e))


async def test_capability_categories(conn: asyncpg.Connection, results: TestResult) -> Dict[str, int]:
    """Test 8: Capabilities by category"""
    try:
        categories = await conn.fetch("""
            SELECT category, COUNT(*) as count 
            FROM capabilities 
            GROUP BY category 
            ORDER BY category
        """)
        
        category_counts = {row['category']: row['count'] for row in categories}
        
        expected_categories = [
            'auth', 'org', 'partner', 'commodity', 'location', 'availability',
            'requirement', 'matching', 'settings', 'invoice', 'contract',
            'payment', 'shipment', 'admin', 'audit', 'data', 'public', 'system'
        ]
        
        missing = [cat for cat in expected_categories if cat not in category_counts]
        if missing:
            results.fail_test("Capability Categories",
                            f"Missing categories: {', '.join(missing)}")
        else:
            total = sum(category_counts.values())
            results.pass_test(f"Capability Categories ({len(category_counts)} categories, {total} total)")
            
        return category_counts
    except Exception as e:
        results.fail_test("Capability Categories", str(e))
        return {}


async def test_no_expired_capabilities(conn: asyncpg.Connection, user: Dict, results: TestResult):
    """Test 9: No expired capabilities"""
    try:
        if not user:
            results.fail_test("No Expired Capabilities", "No user data")
            return
            
        expired = await conn.fetchval("""
            SELECT COUNT(*) FROM user_capabilities 
            WHERE user_id = $1 AND expires_at IS NOT NULL AND expires_at < NOW()
        """, user['id'])
        
        if expired == 0:
            results.pass_test("No Expired Capabilities")
        else:
            results.fail_test("No Expired Capabilities", f"Found {expired} expired capabilities")
    except Exception as e:
        results.fail_test("No Expired Capabilities", str(e))


async def test_database_tables(conn: asyncpg.Connection, results: TestResult):
    """Test 10: Required database tables exist"""
    try:
        required_tables = [
            'users', 'capabilities', 'user_capabilities',
            'roles', 'role_capabilities', 'user_roles'
        ]
        
        existing_tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' AND tablename = ANY($1)
        """, required_tables)
        
        existing = [row['tablename'] for row in existing_tables]
        missing = [t for t in required_tables if t not in existing]
        
        if missing:
            results.fail_test("Database Tables", f"Missing tables: {', '.join(missing)}")
        else:
            results.pass_test(f"Database Tables ({len(required_tables)} tables)")
    except Exception as e:
        results.fail_test("Database Tables", str(e))


async def test_docker_services(results: TestResult):
    """Test 11: Docker services running"""
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        services = result.stdout.strip().split('\n')
        required = ['postgres', 'redis', 'rabbitmq']
        
        running = []
        for service in required:
            if any(service in name for name in services):
                running.append(service)
        
        missing = [s for s in required if s not in running]
        
        if missing:
            results.fail_test("Docker Services", f"Missing services: {', '.join(missing)}")
        else:
            results.pass_test(f"Docker Services ({len(running)}/{len(required)} running)")
    except Exception as e:
        results.fail_test("Docker Services", str(e))


async def test_redis_connection(results: TestResult):
    """Test 12: Redis connection"""
    try:
        import redis.asyncio as redis
        client = await redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        await client.ping()
        await client.aclose()
        results.pass_test("Redis Connection")
    except Exception as e:
        results.fail_test("Redis Connection", str(e))


async def test_capability_uniqueness(conn: asyncpg.Connection, results: TestResult):
    """Test 13: All capabilities are unique"""
    try:
        duplicates = await conn.fetch("""
            SELECT name, COUNT(*) as count 
            FROM capabilities 
            GROUP BY name 
            HAVING COUNT(*) > 1
        """)
        
        if duplicates:
            dup_names = [row['name'] for row in duplicates]
            results.fail_test("Capability Uniqueness", 
                            f"Duplicate capabilities: {', '.join(dup_names)}")
        else:
            results.pass_test("Capability Uniqueness")
    except Exception as e:
        results.fail_test("Capability Uniqueness", str(e))


async def test_superadmin_uniqueness(conn: asyncpg.Connection, results: TestResult):
    """Test 14: Only one SUPER_ADMIN exists"""
    try:
        count = await conn.fetchval("""
            SELECT COUNT(*) FROM users WHERE user_type = 'SUPER_ADMIN'
        """)
        
        if count == 1:
            results.pass_test("SUPER_ADMIN Uniqueness")
        else:
            results.fail_test("SUPER_ADMIN Uniqueness", 
                            f"Expected 1 SUPER_ADMIN, found {count}")
    except Exception as e:
        results.fail_test("SUPER_ADMIN Uniqueness", str(e))


async def test_capability_names_valid(conn: asyncpg.Connection, results: TestResult):
    """Test 15: Capability names sanity (non-empty)"""
    try:
        capabilities = await conn.fetch("SELECT name FROM capabilities")
        non_empty = [cap['name'] for cap in capabilities if cap['name'] and cap['name'].strip()]
        if len(non_empty) != len(capabilities):
            results.fail_test("Capability Names Valid", "Found empty capability names")
        else:
            results.pass_test("Capability Names Valid")
    except Exception as e:
        results.fail_test("Capability Names Valid", str(e))


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SUPER_ADMIN SYSTEM COMPREHENSIVE TEST")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    results = TestResult()
    conn = None
    
    try:
        # Test 1: Database connection
        conn = await test_database_connection(results)
        
        # Test 2: SUPER_ADMIN user exists
        user = await test_superadmin_user_exists(conn, results)
        
        # Test 3: Password verification
        await test_password_verification(user, results)
        
        # Test 4: Data isolation
        await test_data_isolation(user, results)
        
        # Test 5: User active
        await test_user_active(user, results)
        
        # Test 6: Capabilities seeded
        cap_count = await test_capabilities_seeded(conn, results)
        
        # Test 7: SUPER_ADMIN capabilities
        await test_superadmin_capabilities(conn, user, results)
        
        # Test 8: Capability categories
        categories = await test_capability_categories(conn, results)
        
        # Test 9: No expired capabilities
        await test_no_expired_capabilities(conn, user, results)
        
        # Test 10: Database tables
        await test_database_tables(conn, results)
        
        # Test 11: Docker services
        await test_docker_services(results)
        
        # Test 12: Redis connection
        await test_redis_connection(results)
        
        # Test 13: Capability uniqueness
        await test_capability_uniqueness(conn, results)
        
        # Test 14: SUPER_ADMIN uniqueness
        await test_superadmin_uniqueness(conn, results)
        
        # Test 15: Capability names valid
        await test_capability_names_valid(conn, results)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        results.fail_test("Critical Error", str(e))
    finally:
        if conn:
            await conn.close()
    
    # Print summary
    success = results.summary()
    
    print(f"\n{'='*80}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
