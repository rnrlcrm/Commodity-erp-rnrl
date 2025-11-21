"""
Audit Service

Provides audit trail queries and reports.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.events.store import EventStore


class AuditEntry(BaseModel):
    """Audit trail entry for UI display"""
    
    event_id: uuid.UUID
    event_type: str
    user_id: uuid.UUID
    timestamp: datetime
    action: str  # Human-readable action
    entity_type: str
    entity_id: uuid.UUID
    changes: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class AuditService:
    """
    Service for querying audit trails.
    
    Provides high-level queries for:
    - Entity history
    - User activity
    - Change reports
    - Compliance audits
    """
    
    def __init__(self, session: AsyncSession):
        self.store = EventStore(session)
    
    async def get_entity_history(
        self,
        entity_id: uuid.UUID,
        entity_type: str,
    ) -> List[AuditEntry]:
        """
        Get complete change history for an entity.
        
        Example: "Show me all changes to Organization X"
        """
        events = await self.store.get_by_aggregate(entity_id, entity_type)
        
        return [
            AuditEntry(
                event_id=event.id,
                event_type=event.event_type,
                user_id=event.user_id,
                timestamp=event.timestamp,
                action=self._format_action(event.event_type),
                entity_type=event.aggregate_type,
                entity_id=event.aggregate_id,
                changes=event.data,
                metadata=event.metadata,
            )
            for event in events
        ]
    
    async def get_user_activity(
        self,
        user_id: uuid.UUID,
        limit: Optional[int] = 100,
    ) -> List[AuditEntry]:
        """
        Get all actions performed by a user.
        
        Example: "Show me what User X did today"
        """
        events = await self.store.get_by_user(user_id, limit)
        
        return [
            AuditEntry(
                event_id=event.id,
                event_type=event.event_type,
                user_id=event.user_id,
                timestamp=event.timestamp,
                action=self._format_action(event.event_type),
                entity_type=event.aggregate_type,
                entity_id=event.aggregate_id,
                changes=event.data,
                metadata=event.metadata,
            )
            for event in events
        ]
    
    async def get_recent_changes(
        self,
        entity_type: Optional[str] = None,
        hours: int = 24,
    ) -> List[AuditEntry]:
        """
        Get recent changes across the system.
        
        Example: "Show me all commodity changes in last 24 hours"
        """
        from datetime import timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        events = await self.store.get_by_time_range(
            start_time=start_time,
            end_time=end_time,
            aggregate_type=entity_type,
        )
        
        return [
            AuditEntry(
                event_id=event.id,
                event_type=event.event_type,
                user_id=event.user_id,
                timestamp=event.timestamp,
                action=self._format_action(event.event_type),
                entity_type=event.aggregate_type,
                entity_id=event.aggregate_id,
                changes=event.data,
                metadata=event.metadata,
            )
            for event in events
        ]
    
    async def get_change_count(
        self,
        entity_id: uuid.UUID,
        entity_type: Optional[str] = None,
    ) -> int:
        """Get total number of changes to an entity"""
        return await self.store.count_by_aggregate(entity_id, entity_type)
    
    def _format_action(self, event_type: str) -> str:
        """Convert event type to human-readable action"""
        # Split on dot: "organization.created" -> "Organization Created"
        parts = event_type.split(".")
        if len(parts) == 2:
            entity, action = parts
            return f"{entity.title()} {action.title()}"
        return event_type.replace("_", " ").title()
