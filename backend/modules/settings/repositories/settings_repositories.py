from __future__ import annotations

from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.organization.models import Organization
from backend.modules.settings.models.settings_models import (
	Permission,
	Role,
	RolePermission,
	User,
	UserRole,
	RefreshToken,
)


class BaseRepo:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db


class OrganizationRepository(BaseRepo):
	async def get_by_name(self, name: str) -> Optional[Organization]:
		result = await self.db.execute(select(Organization).where(Organization.name == name))
		return result.scalar_one_or_none()

	async def create(self, name: str, code: Optional[str] = None) -> Organization:
		obj = Organization(name=name, code=code)
		self.db.add(obj)
		await self.db.flush()
		return obj


class UserRepository(BaseRepo):
	async def get_by_id(self, user_id: str | UUID) -> Optional[User]:
		return await self.db.get(User, user_id)

	async def get_by_email(self, email: str) -> Optional[User]:
		result = await self.db.execute(select(User).where(User.email == email))
		return result.scalar_one_or_none()
	
	async def get_by_mobile(self, mobile_number: str) -> Optional[User]:
		"""Get user by mobile number."""
		result = await self.db.execute(select(User).where(User.mobile_number == mobile_number))
		return result.scalar_one_or_none()

	async def get_first(self) -> Optional[User]:
		result = await self.db.execute(select(User).limit(1))
		return result.scalar_one_or_none()

	async def create(self, organization_id: UUID, email: str, full_name: Optional[str], password_hash: str) -> User:
		obj = User(organization_id=organization_id, email=email, full_name=full_name, password_hash=password_hash)
		self.db.add(obj)
		await self.db.flush()
		return obj

	async def get_sub_users(self, parent_user_id: UUID) -> list[User]:
		"""Get all sub-users for a parent user."""
		result = await self.db.execute(
			select(User).where(User.parent_user_id == parent_user_id)
		)
		return list(result.scalars().all())

	async def count_sub_users(self, parent_user_id: UUID) -> int:
		"""Count sub-users for a parent user."""
		from sqlalchemy import func
		result = await self.db.execute(
			select(func.count()).select_from(User).where(User.parent_user_id == parent_user_id)
		)
		return result.scalar_one()

	async def create_sub_user(
		self,
		parent_user_id: UUID,
		mobile_number: str,
		full_name: str,
		pin_hash: Optional[str] = None,
		role: Optional[str] = None
	) -> User:
		"""
		Create a sub-user with parent relationship.
		Sub-users login via mobile OTP or PIN (not email/password).
		"""
		# Get parent user to inherit business_partner_id
		parent = await self.get_by_id(parent_user_id)
		if not parent:
			raise ValueError("Parent user not found")
		
		# Parent must be EXTERNAL user (business partner user)
		if parent.user_type != 'EXTERNAL':
			raise ValueError("Only EXTERNAL users (business partners) can create sub-users")
		
		# Check if parent is already a sub-user (no recursive sub-users)
		if parent.parent_user_id is not None:
			raise ValueError("Sub-users cannot create their own sub-users")
		
		# Check sub-user limit (max 2)
		count = await self.count_sub_users(parent_user_id)
		if count >= 2:
			raise ValueError("Maximum of 2 sub-users per parent reached")
		
		# Check for duplicate mobile number
		existing = await self.get_by_mobile(mobile_number)
		if existing:
			raise ValueError("Mobile number already registered")
		
		obj = User(
			user_type='EXTERNAL',  # Sub-users are always EXTERNAL
			business_partner_id=parent.business_partner_id,  # Inherit from parent
			mobile_number=mobile_number,
			full_name=full_name,
			pin_hash=pin_hash,  # Optional secure PIN
			password_hash=None,  # No password for EXTERNAL users
			parent_user_id=parent_user_id,
			role=role,
			is_active=True,
			is_verified=False  # Will be verified on first OTP login
		)
		self.db.add(obj)
		await self.db.flush()
		return obj

	async def disable_sub_user(self, sub_user_id: UUID) -> None:
		"""Disable a sub-user (sets is_active = False)."""
		user = await self.get_by_id(sub_user_id)
		if not user:
			raise ValueError("Sub-user not found")
		if user.parent_user_id is None:
			raise ValueError("Cannot disable - user is not a sub-user")
		user.is_active = False
		self.db.add(user)

	async def enable_sub_user(self, sub_user_id: UUID) -> None:
		"""Enable a sub-user (sets is_active = True)."""
		user = await self.get_by_id(sub_user_id)
		if not user:
			raise ValueError("Sub-user not found")
		if user.parent_user_id is None:
			raise ValueError("Cannot enable - user is not a sub-user")
		user.is_active = True
		self.db.add(user)

	async def enable_2fa(self, user_id: UUID, pin_hash: str) -> None:
		"""Enable 2FA and set PIN hash for a user."""
		user = await self.get_by_id(user_id)
		if not user:
			raise ValueError("User not found")
		user.two_fa_enabled = True
		user.pin_hash = pin_hash
		self.db.add(user)

	async def disable_2fa(self, user_id: UUID) -> None:
		"""Disable 2FA and clear PIN hash for a user."""
		user = await self.get_by_id(user_id)
		if not user:
			raise ValueError("User not found")
		user.two_fa_enabled = False
		user.pin_hash = None
		self.db.add(user)


class RoleRepository(BaseRepo):
	async def get_by_name(self, name: str) -> Optional[Role]:
		result = await self.db.execute(select(Role).where(Role.name == name))
		return result.scalar_one_or_none()

	async def create(self, name: str, description: Optional[str] = None) -> Role:
		obj = Role(name=name, description=description)
		self.db.add(obj)
		await self.db.flush()
		return obj


class PermissionRepository(BaseRepo):
	async def get_by_code(self, code: str) -> Optional[Permission]:
		result = await self.db.execute(select(Permission).where(Permission.code == code))
		return result.scalar_one_or_none()

	async def ensure_many(self, codes: Iterable[str]) -> list[Permission]:
		result = await self.db.execute(select(Permission).where(Permission.code.in_(list(codes))))
		existing = result.scalars().all()
		existing_codes = {p.code for p in existing}
		created: list[Permission] = []
		for code in codes:
			if code not in existing_codes:
				p = Permission(code=code)
				self.db.add(p)
				created.append(p)
		if created:
			await self.db.flush()
		return list(existing) + created


class RolePermissionRepository(BaseRepo):
	async def ensure(self, role_id: UUID, permission_ids: Iterable[UUID]) -> None:
		for pid in permission_ids:
			rp = await self.db.get(RolePermission, {"role_id": role_id, "permission_id": pid})
			if rp is None:
				self.db.add(RolePermission(role_id=role_id, permission_id=pid))


class UserRoleRepository(BaseRepo):
	async def ensure(self, user_id: UUID, role_id: UUID) -> None:
		ur = await self.db.get(UserRole, {"user_id": user_id, "role_id": role_id})
		if ur is None:
			self.db.add(UserRole(user_id=user_id, role_id=role_id))


class RefreshTokenRepository(BaseRepo):
	async def get_by_jti(self, jti: str) -> RefreshToken | None:
		result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
		return result.scalar_one_or_none()

	async def create(self, user_id: UUID, jti: str, expires_at) -> RefreshToken:  # noqa: ANN001
		obj = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at, revoked=False)
		self.db.add(obj)
		await self.db.flush()
		return obj

	async def revoke(self, token: RefreshToken) -> None:
		token.revoked = True
		self.db.add(token)

