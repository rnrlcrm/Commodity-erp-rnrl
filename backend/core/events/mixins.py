"""
Event Mixin for Domain Models

Provides event emission capabilities to domain models for audit trail and event sourcing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from backend.core.events.base import BaseEvent


class EventMixin:
    """
    Mixin to add event emission capabilities to domain models.
    
    Usage:
        class Commodity(Base, EventMixin):
            __tablename__ = "commodities"
            id = Column(UUID, primary_key=True)
            name = Column(String)
            
            def after_create(self, user_id: UUID):
                self.emit_event("commodity.created", user_id, self.to_dict())
    """
    
    # Class-level registry of pending events (per instance)
    _pending_events: list[BaseEvent] = []
    
    def emit_event(
        self,
        event_type: str,
        user_id: UUID,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit a domain event.
        
        Args:
            event_type: Event type (e.g., "commodity.created", "trade.executed")
            user_id: ID of user who triggered the event
            data: Event payload data
            metadata: Optional metadata (IP, user agent, etc.)
        """
        from backend.core.events.base import BaseEvent, EventMetadata
        
        event = BaseEvent(
            event_type=event_type,
            aggregate_id=self.id,  # type: ignore
            aggregate_type=self.__class__.__name__,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            version=1,
            data=data,
            metadata=EventMetadata(**metadata) if metadata else None
        )
        
        # Store event for later persistence
        if not hasattr(self, '_pending_events'):
            self._pending_events = []
        self._pending_events.append(event)
    
    async def flush_events(self, db: AsyncSession) -> None:
        """
        Persist all pending events to event store.
        
        Args:
            db: Async database session
        """
        if not hasattr(self, '_pending_events') or not self._pending_events:
            return
        
        from backend.core.events.store import EventStore
        
        store = EventStore(db)
        for event in self._pending_events:
            await store.save(event)
        
        # Clear pending events
        self._pending_events = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for event payload.
        Override this in your models to customize serialization.
        
        Returns:
            Dictionary representation of the model
        """
        from sqlalchemy.inspection import inspect
        
        # Get all columns
        mapper = inspect(self.__class__)
        result = {}
        
        for column in mapper.columns:
            value = getattr(self, column.name)
            
            # Convert UUID to string
            if isinstance(value, UUID):
                result[column.name] = str(value)
            # Convert datetime to ISO format
            elif isinstance(value, datetime):
                result[column.name] = value.isoformat()
            # Keep primitives as-is
            else:
                result[column.name] = value
        
        return result
