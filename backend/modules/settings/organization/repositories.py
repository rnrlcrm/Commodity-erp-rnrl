from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.organization.models import (
    Organization,
    OrganizationBankAccount,
    OrganizationDocumentSeries,
    OrganizationFinancialYear,
    OrganizationGST,
)


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Organization:
        org = Organization(**kwargs)
        self.db.add(org)
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        result = await self.db.execute(
            select(Organization).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, org_id: UUID, **kwargs) -> Optional[Organization]:
        org = await self.get_by_id(org_id)
        if not org:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(org, key, value)
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def delete(self, org_id: UUID) -> bool:
        org = await self.get_by_id(org_id)
        if not org:
            return False
        await self.db.delete(org)
        await self.db.flush()
        return True


class OrganizationGSTRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> OrganizationGST:
        gst = OrganizationGST(**kwargs)
        self.db.add(gst)
        await self.db.flush()
        await self.db.refresh(gst)
        return gst

    async def get_by_id(self, gst_id: UUID) -> Optional[OrganizationGST]:
        result = await self.db.execute(
            select(OrganizationGST).where(OrganizationGST.id == gst_id)
        )
        return result.scalar_one_or_none()

    async def get_by_gstin(self, gstin: str) -> Optional[OrganizationGST]:
        result = await self.db.execute(
            select(OrganizationGST).where(OrganizationGST.gstin == gstin)
        )
        return result.scalar_one_or_none()

    async def get_primary(self, org_id: UUID) -> Optional[OrganizationGST]:
        result = await self.db.execute(
            select(OrganizationGST).where(
                and_(
                    OrganizationGST.organization_id == org_id,
                    OrganizationGST.is_primary == True,
                    OrganizationGST.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: UUID) -> list[OrganizationGST]:
        result = await self.db.execute(
            select(OrganizationGST).where(OrganizationGST.organization_id == org_id)
        )
        return list(result.scalars().all())

    async def update(self, gst_id: UUID, **kwargs) -> Optional[OrganizationGST]:
        gst = await self.get_by_id(gst_id)
        if not gst:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(gst, key, value)
        await self.db.flush()
        await self.db.refresh(gst)
        return gst

    async def delete(self, gst_id: UUID) -> bool:
        gst = await self.get_by_id(gst_id)
        if not gst:
            return False
        await self.db.delete(gst)
        await self.db.flush()
        return True


class OrganizationBankAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> OrganizationBankAccount:
        account = OrganizationBankAccount(**kwargs)
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def get_by_id(self, account_id: UUID) -> Optional[OrganizationBankAccount]:
        result = await self.db.execute(
            select(OrganizationBankAccount).where(OrganizationBankAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_default(self, org_id: UUID) -> Optional[OrganizationBankAccount]:
        result = await self.db.execute(
            select(OrganizationBankAccount).where(
                and_(
                    OrganizationBankAccount.organization_id == org_id,
                    OrganizationBankAccount.is_default == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: UUID) -> list[OrganizationBankAccount]:
        result = await self.db.execute(
            select(OrganizationBankAccount).where(OrganizationBankAccount.organization_id == org_id)
        )
        return list(result.scalars().all())

    async def update(self, account_id: UUID, **kwargs) -> Optional[OrganizationBankAccount]:
        account = await self.get_by_id(account_id)
        if not account:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(account, key, value)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def delete(self, account_id: UUID) -> bool:
        account = await self.get_by_id(account_id)
        if not account:
            return False
        await self.db.delete(account)
        await self.db.flush()
        return True


class OrganizationFinancialYearRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> OrganizationFinancialYear:
        fy = OrganizationFinancialYear(**kwargs)
        self.db.add(fy)
        await self.db.flush()
        await self.db.refresh(fy)
        return fy

    async def get_by_id(self, fy_id: UUID) -> Optional[OrganizationFinancialYear]:
        result = await self.db.execute(
            select(OrganizationFinancialYear).where(OrganizationFinancialYear.id == fy_id)
        )
        return result.scalar_one_or_none()

    async def get_active(self, org_id: UUID) -> Optional[OrganizationFinancialYear]:
        result = await self.db.execute(
            select(OrganizationFinancialYear).where(
                and_(
                    OrganizationFinancialYear.organization_id == org_id,
                    OrganizationFinancialYear.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: UUID) -> list[OrganizationFinancialYear]:
        result = await self.db.execute(
            select(OrganizationFinancialYear)
            .where(OrganizationFinancialYear.organization_id == org_id)
            .order_by(OrganizationFinancialYear.start_date.desc())
        )
        return list(result.scalars().all())

    async def update(self, fy_id: UUID, **kwargs) -> Optional[OrganizationFinancialYear]:
        fy = await self.get_by_id(fy_id)
        if not fy:
            return None
        
        # Check version for optimistic locking
        if "version" in kwargs:
            expected_version = kwargs.pop("version")
            if fy.version != expected_version:
                raise ValueError(f"Version conflict: expected {expected_version}, found {fy.version}")
            fy.version += 1
        
        for key, value in kwargs.items():
            if value is not None:
                setattr(fy, key, value)
        await self.db.flush()
        await self.db.refresh(fy)
        return fy

    async def delete(self, fy_id: UUID) -> bool:
        fy = await self.get_by_id(fy_id)
        if not fy:
            return False
        await self.db.delete(fy)
        await self.db.flush()
        return True


class OrganizationDocumentSeriesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> OrganizationDocumentSeries:
        series = OrganizationDocumentSeries(**kwargs)
        self.db.add(series)
        await self.db.flush()
        await self.db.refresh(series)
        return series

    async def get_by_id(self, series_id: UUID) -> Optional[OrganizationDocumentSeries]:
        result = await self.db.execute(
            select(OrganizationDocumentSeries).where(OrganizationDocumentSeries.id == series_id)
        )
        return result.scalar_one_or_none()

    async def get_by_type(
        self, org_id: UUID, fy_id: UUID, doc_type: str
    ) -> Optional[OrganizationDocumentSeries]:
        result = await self.db.execute(
            select(OrganizationDocumentSeries).where(
                and_(
                    OrganizationDocumentSeries.organization_id == org_id,
                    OrganizationDocumentSeries.financial_year_id == fy_id,
                    OrganizationDocumentSeries.document_type == doc_type,
                    OrganizationDocumentSeries.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: UUID) -> list[OrganizationDocumentSeries]:
        result = await self.db.execute(
            select(OrganizationDocumentSeries).where(OrganizationDocumentSeries.organization_id == org_id)
        )
        return list(result.scalars().all())

    async def list_by_financial_year(self, fy_id: UUID) -> list[OrganizationDocumentSeries]:
        result = await self.db.execute(
            select(OrganizationDocumentSeries).where(OrganizationDocumentSeries.financial_year_id == fy_id)
        )
        return list(result.scalars().all())

    async def increment_number(self, series_id: UUID) -> Optional[OrganizationDocumentSeries]:
        """Atomically increment document number and return updated series."""
        series = await self.get_by_id(series_id)
        if not series:
            return None
        series.current_number += 1
        await self.db.flush()
        await self.db.refresh(series)
        return series

    async def update(self, series_id: UUID, **kwargs) -> Optional[OrganizationDocumentSeries]:
        series = await self.get_by_id(series_id)
        if not series:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(series, key, value)
        self.db.flush()
        self.db.refresh(series)
        return series

    def delete(self, series_id: UUID) -> bool:
        series = self.get_by_id(series_id)
        if not series:
            return False
        self.db.delete(series)
        self.db.flush()
        return True
