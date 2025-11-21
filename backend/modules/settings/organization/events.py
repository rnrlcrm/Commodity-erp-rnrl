"""
Organization Module Events

Defines all events that can occur in the organization module.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from backend.core.events.base import BaseEvent, EventMetadata


class OrganizationCreated(BaseEvent):
    """Emitted when a new organization is created"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.created",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationUpdated(BaseEvent):
    """Emitted when organization details are updated"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],  # Should include 'changes' dict with before/after
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.updated",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationDeleted(BaseEvent):
    """Emitted when organization is soft-deleted"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.deleted",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationGSTAdded(BaseEvent):
    """Emitted when GST registration is added"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,  # organization_id
        user_id: uuid.UUID,
        data: Dict[str, Any],  # GST details
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.gst.added",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationGSTUpdated(BaseEvent):
    """Emitted when GST registration is updated"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.gst.updated",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationBankAccountAdded(BaseEvent):
    """Emitted when bank account is added"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.bank_account.added",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationBankAccountUpdated(BaseEvent):
    """Emitted when bank account is updated"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.bank_account.updated",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationFinancialYearAdded(BaseEvent):
    """Emitted when financial year is configured"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.financial_year.added",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )


class OrganizationDocumentSeriesAdded(BaseEvent):
    """Emitted when document series is configured"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(
            event_type="organization.document_series.added",
            aggregate_id=aggregate_id,
            aggregate_type="organization",
            user_id=user_id,
            data=data,
            metadata=metadata,
        )
