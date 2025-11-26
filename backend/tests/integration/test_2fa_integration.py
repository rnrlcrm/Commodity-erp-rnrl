"""
2FA Integration Tests

Tests the complete 2FA (Two-Factor Authentication) functionality with PIN:
- Setting up 2FA (enabling and setting PIN)
- Verifying PIN during login
- Disabling 2FA
- Login flow with 2FA enabled
- Invalid PIN attempts
- PIN validation (4-6 digits)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.models.settings_models import User
from backend.core.auth.passwords import PasswordHasher

pwd_hasher = PasswordHasher()


class Test2FASetup:
    """Test 2FA setup functionality."""

    @pytest.mark.asyncio
    async def test_setup_2fa_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: User can successfully enable 2FA with valid PIN."""
        # Create and login user
        user = User(
            email="user1@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="User One",
            organization_id=seed_organization.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "user1@example.com", "password": "Password123!"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        # Setup 2FA with 4-digit PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "1234"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["two_fa_enabled"] is True
        assert "enabled successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_setup_2fa_with_6_digit_pin(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: User can enable 2FA with 6-digit PIN."""
        user = User(
            email="user2@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="User Two",
            organization_id=seed_organization.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "user2@example.com", "password": "Password123!"}
        )
        access_token = login_response.json()["access_token"]

        # Setup 2FA with 6-digit PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "123456"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["two_fa_enabled"] is True

    @pytest.mark.asyncio
    async def test_setup_2fa_invalid_pin_too_short(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """❌ Test: Cannot enable 2FA with PIN shorter than 4 digits."""
        user = User(
            email="user3@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="User Three",
            organization_id=seed_organization.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "user3@example.com", "password": "Password123!"}
        )
        access_token = login_response.json()["access_token"]

        # Try to setup 2FA with 3-digit PIN (invalid)
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "123"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_setup_2fa_invalid_pin_too_long(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """❌ Test: Cannot enable 2FA with PIN longer than 6 digits."""
        user = User(
            email="user4@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="User Four",
            organization_id=seed_organization.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "user4@example.com", "password": "Password123!"}
        )
        access_token = login_response.json()["access_token"]

        # Try to setup 2FA with 7-digit PIN (invalid)
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "1234567"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_setup_2fa_invalid_pin_non_numeric(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """❌ Test: Cannot enable 2FA with non-numeric PIN."""
        user = User(
            email="user5@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="User Five",
            organization_id=seed_organization.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "user5@example.com", "password": "Password123!"}
        )
        access_token = login_response.json()["access_token"]

        # Try to setup 2FA with alphanumeric PIN (invalid)
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "12ab"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 422  # Validation error


class Test2FALogin:
    """Test login flow with 2FA enabled."""

    @pytest.mark.asyncio
    async def test_login_with_2fa_enabled_requires_pin(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: Login with 2FA enabled returns 2FA required response."""
        # Create user and enable 2FA
        user = User(
            email="2fauser@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="2FA User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("1234")
        )
        db_session.add(user)
        await db_session.flush()

        # Try to login
        response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "2fauser@example.com", "password": "Password123!"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["two_fa_required"] is True
        assert "verify with PIN" in data["message"]
        assert data["email"] == "2fauser@example.com"
        assert "access_token" not in data  # No token until PIN verified

    @pytest.mark.asyncio
    async def test_verify_pin_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: Verifying correct PIN returns access tokens."""
        # Create user with 2FA enabled
        user = User(
            email="verify@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="Verify User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("5678")
        )
        db_session.add(user)
        await db_session.flush()

        # Verify PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "verify@example.com", "pin": "5678"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_verify_pin_fail_invalid_pin(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """❌ Test: Verifying incorrect PIN fails."""
        # Create user with 2FA enabled
        user = User(
            email="wrongpin@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="Wrong PIN User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("9999")
        )
        db_session.add(user)
        await db_session.flush()

        # Try to verify with wrong PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "wrongpin@example.com", "pin": "0000"}
        )

        assert response.status_code == 401
        assert "Invalid PIN" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_verify_pin_fail_2fa_not_enabled(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """❌ Test: Cannot verify PIN for user without 2FA enabled."""
        # Create user without 2FA
        user = User(
            email="no2fa@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="No 2FA User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=False
        )
        db_session.add(user)
        await db_session.flush()

        # Try to verify PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "no2fa@example.com", "pin": "1234"}
        )

        assert response.status_code == 401
        assert "2FA not enabled" in response.json()["detail"]


class Test2FADisable:
    """Test 2FA disable functionality."""

    @pytest.mark.asyncio
    async def test_disable_2fa_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: User can successfully disable 2FA."""
        # Create user with 2FA enabled
        user = User(
            email="disable@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="Disable User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("1111")
        )
        db_session.add(user)
        await db_session.flush()

        # Login (should require PIN)
        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "disable@example.com", "password": "Password123!"}
        )
        assert login_response.json()["two_fa_required"] is True

        # Verify PIN to get access token
        verify_response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "disable@example.com", "pin": "1111"}
        )
        access_token = verify_response.json()["access_token"]

        # Disable 2FA
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-disable",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["two_fa_enabled"] is False
        assert "disabled successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_login_after_2fa_disabled(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: After disabling 2FA, login works without PIN."""
        # Create user with 2FA enabled
        user = User(
            email="testdisable@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="Test Disable",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("2222")
        )
        db_session.add(user)
        await db_session.flush()

        # Verify PIN to get token
        verify_response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "testdisable@example.com", "pin": "2222"}
        )
        access_token = verify_response.json()["access_token"]

        # Disable 2FA
        await async_client.post(
            "/api/v1/settings/auth/2fa-disable",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Try to login again (should work without PIN now)
        login_response = await async_client.post(
            "/api/v1/settings/auth/login",
            json={"email": "testdisable@example.com", "password": "Password123!"}
        )

        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data  # Direct token, no 2FA required
        assert "two_fa_required" not in data or data.get("two_fa_required") is False


class Test2FAUpdatePIN:
    """Test updating 2FA PIN."""

    @pytest.mark.asyncio
    async def test_update_pin_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_organization
    ):
        """✅ Test: User can update their 2FA PIN."""
        # Create user with 2FA enabled
        user = User(
            email="updatepin@example.com",
            password_hash=pwd_hasher.hash("Password123!"),
            full_name="Update PIN User",
            organization_id=seed_organization.id,
            is_active=True,
            two_fa_enabled=True,
            pin_hash=pwd_hasher.hash("3333")
        )
        db_session.add(user)
        await db_session.flush()

        # Get access token
        verify_response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "updatepin@example.com", "pin": "3333"}
        )
        access_token = verify_response.json()["access_token"]

        # Update PIN
        response = await async_client.post(
            "/api/v1/settings/auth/2fa-setup",
            json={"pin": "4444"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200

        # Verify old PIN no longer works
        old_pin_response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "updatepin@example.com", "pin": "3333"}
        )
        assert old_pin_response.status_code == 401

        # Verify new PIN works
        new_pin_response = await async_client.post(
            "/api/v1/settings/auth/2fa-verify",
            json={"email": "updatepin@example.com", "pin": "4444"}
        )
        assert new_pin_response.status_code == 200
        assert "access_token" in new_pin_response.json()
