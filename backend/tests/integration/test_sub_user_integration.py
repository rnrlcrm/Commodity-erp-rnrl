"""
Sub-User Integration Tests

Tests the complete sub-user functionality:
- Creating sub-users (max 2 per parent)
- Listing sub-users
- Deleting sub-users
- Validation rules (no recursive sub-users, max limit)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.models.settings_models import User
from backend.core.auth.passwords import PasswordHasher

pwd_hasher = PasswordHasher()


class TestSubUserCreation:
    """Test sub-user creation functionality."""

    @pytest.mark.asyncio
    async def test_create_sub_user_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Parent user can create a sub-user."""
        # Create EXTERNAL parent user (business partner)
        parent = User(
            mobile_number="+919876543210",
            full_name="Parent User",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()
        
        # For testing, we need to authenticate - create a token manually
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create sub-user
        response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={
                "mobile_number": "+919876543211",
                "full_name": "Sub User 1",
                "role": "assistant"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["mobile_number"] == "+919876543211"
        assert data["full_name"] == "Sub User 1"
        assert data["role"] == "assistant"
        assert data["is_active"] is True
        assert data["parent_user_id"] == str(parent.id)
        assert data["business_partner_id"] == str(seed_business_partner.id)
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_second_sub_user_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Parent can create a second sub-user (max 2)."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543220",
            full_name="Parent User 2",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create first sub-user
        response1 = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={
                "mobile_number": "+919876543221",
                "full_name": "Sub User 2A"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response1.status_code == 201

        # Create second sub-user (will now see first one in DB)
        response2 = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={
                "mobile_number": "+919876543222",
                "full_name": "Sub User 2B"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response2.status_code == 201
        assert response2.json()["mobile_number"] == "+919876543222"

    @pytest.mark.asyncio
    async def test_create_third_sub_user_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Cannot create more than 2 sub-users per parent."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543230",
            full_name="Parent User 3",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create first sub-user
        await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543231", "full_name": "Sub 3A"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Create second sub-user
        await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543232", "full_name": "Sub 3B"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Try to create third sub-user (should fail)
        response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543233", "full_name": "Sub 3C"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 400
        assert "Maximum of 2 sub-users" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_sub_user_cannot_create_sub_user(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Sub-users cannot create their own sub-users (no recursion)."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543240",
            full_name="Parent User 4",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create parent token
        from backend.core.auth.jwt import create_token
        parent_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create sub-user
        sub_response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543241", "full_name": "Sub 4"},
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        sub_user_id = sub_response.json()["id"]
        
        # Create token for sub-user
        sub_token = create_token(
            sub_user_id,
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Try to create sub-sub-user (should fail)
        response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543242", "full_name": "Sub Sub"},
            headers={"Authorization": f"Bearer {sub_token}"}
        )

        assert response.status_code == 400
        assert "cannot create their own sub-users" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_sub_user_duplicate_mobile_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Cannot create sub-user with duplicate mobile number."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543250",
            full_name="Parent User 5",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create first sub-user
        await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543251", "full_name": "First"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Try to create second sub-user with same mobile
        response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543251", "full_name": "Second"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 400
        assert "Mobile number already registered" in response.json()["detail"]


class TestSubUserListing:
    """Test listing sub-users functionality."""

    @pytest.mark.asyncio
    async def test_list_sub_users_empty(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Parent with no sub-users gets empty list."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543260",
            full_name="Parent User 6",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # List sub-users
        response = await async_client.get(
            "/api/v1/settings/auth/sub-users",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_sub_users_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Parent can list their sub-users."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543270",
            full_name="Parent User 7",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create two sub-users
        await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543271", "full_name": "Sub 7A", "role": "manager"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543272", "full_name": "Sub 7B", "role": "assistant"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # List sub-users
        response = await async_client.get(
            "/api/v1/settings/auth/sub-users",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        mobiles = {sub["mobile_number"] for sub in data}
        assert "+919876543271" in mobiles
        assert "+919876543272" in mobiles
        
        # Verify all have correct parent_user_id and business_partner_id
        for sub in data:
            assert sub["parent_user_id"] == str(parent.id)
            assert sub["business_partner_id"] == str(seed_business_partner.id)
            assert sub["is_active"] is True


class TestSubUserDeletion:
    """Test deleting sub-users functionality."""

    @pytest.mark.asyncio
    async def test_delete_sub_user_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Parent can delete their sub-user."""
        # Create EXTERNAL parent user
        parent = User(
            mobile_number="+919876543280",
            full_name="Parent User 8",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent)
        await db_session.flush()

        # Create access token
        from backend.core.auth.jwt import create_token
        access_token = create_token(
            str(parent.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Create sub-user
        create_response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543281", "full_name": "Sub 8"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        sub_user_id = create_response.json()["id"]

        # Delete sub-user
        response = await async_client.delete(
            f"/api/v1/settings/auth/sub-users/{sub_user_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 204

        # Verify sub-user is gone
        list_response = await async_client.get(
            "/api/v1/settings/auth/sub-users",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert len(list_response.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_other_users_sub_user_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Cannot delete another user's sub-user."""
        # Create two EXTERNAL parent users
        parent1 = User(
            mobile_number="+919876543290",
            full_name="Parent 9A",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        parent2 = User(
            mobile_number="+919876543291",
            full_name="Parent 9B",
            user_type="EXTERNAL",
            business_partner_id=seed_business_partner.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(parent1)
        db_session.add(parent2)
        await db_session.flush()

        # Create tokens
        from backend.core.auth.jwt import create_token
        token1 = create_token(
            str(parent1.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )
        token2 = create_token(
            str(parent2.id),
            str(seed_business_partner.id),
            minutes=30,
            token_type="access"
        )

        # Parent1 creates sub-user
        create_response = await async_client.post(
            "/api/v1/settings/auth/sub-users",
            json={"mobile_number": "+919876543292", "full_name": "Sub 9"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        sub_user_id = create_response.json()["id"]

        # Parent2 tries to delete parent1's sub-user
        response = await async_client.delete(
            f"/api/v1/settings/auth/sub-users/{sub_user_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403
        assert "only delete your own sub-users" in response.json()["detail"]


class TestSubUserLogin:
    """Test that sub-users can login independently."""

    @pytest.mark.skip(reason="Sub-users now use mobile OTP login, not password - will be tested in mobile OTP tests")
    @pytest.mark.asyncio
    async def test_sub_user_can_login(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        seed_business_partner
    ):
        """✅ Test: Sub-user can login with mobile OTP (not password)."""
        # TODO: Implement once mobile OTP login is integrated
        # Sub-users are EXTERNAL users and must authenticate via mobile OTP
        # This test should:
        # 1. Create parent user (EXTERNAL)
        # 2. Create sub-user with mobile_number
        # 3. Send OTP to sub-user's mobile
        # 4. Verify OTP and get access token
        # 5. Use token to access /auth/me
        pass

