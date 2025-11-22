"""
Business Partner Model - Minimal version for FK foundation

This is a minimal model providing only what's needed for data isolation.
Full business partner features (KYC, credit management, etc.) will be added later.

Compliance:
- GDPR: Soft delete support (7-year retention)
- IT Act 2000: Audit trail (created_at, updated_at, created_by, updated_by)
- Income Tax Act: 7-year retention via soft delete
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from backend.db.session import Base


class BusinessPartner(Base):
    """
    Business Partner - External companies (buyers, sellers, brokers, transporters).
    
    Minimal model for FK foundation. Full features to be added in dedicated module later.
    """
    
    __tablename__ = "business_partners"
    
    # Primary Key
    id = Column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    
    # Basic Info (minimal)
    name = Column(String(255), nullable=False)
    partner_type = Column(
        String(50),
        nullable=False,
        comment="BUYER, SELLER, BROKER, TRANSPORTER, BOTH"
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit Trail (IT Act 2000 compliance)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_by = Column(PostgreSQLUUID(as_uuid=True), nullable=True)
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    updated_by = Column(PostgreSQLUUID(as_uuid=True), nullable=True)
    
    # Soft Delete (GDPR compliance - 7 year retention)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PostgreSQLUUID(as_uuid=True), nullable=True)
    deletion_reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<BusinessPartner(id={self.id}, name='{self.name}', type='{self.partner_type}')>"
