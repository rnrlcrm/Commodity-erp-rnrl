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

	async def get_first(self) -> Optional[User]:
		result = await self.db.execute(select(User).limit(1))
		return result.scalar_one_or_none()

	async def create(self, organization_id: UUID, email: str, full_name: Optional[str], password_hash: str) -> User:
		obj = User(organization_id=organization_id, email=email, full_name=full_name, password_hash=password_hash)
		self.db.add(obj)
		await self.db.flush()
		return obj


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

