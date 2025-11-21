"""
Base Event Classes

Defines the core event structure used across all modules.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventMetadata(BaseModel):
    """Metadata about the event context"""
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    reason: Optional[str] = None
    correlation_id: Optional[str] = None  # For tracking related events
    extra: Optional[Dict[str, Any]] = None


class BaseEvent(BaseModel):
    """
    Base class for all domain events.
    
    Events are immutable records of things that have happened.
    They provide complete audit trail and enable event sourcing.
    """
    
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str  # e.g., "commodity.created", "trade.executed"
    aggregate_id: uuid.UUID  # ID of the entity this event relates to
    aggregate_type: str  # Type of entity: "commodity", "trade", "organization"
    user_id: uuid.UUID  # Who triggered this event
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1  # Event version for schema evolution
    data: Dict[str, Any]  # The actual event payload
    metadata: Optional[EventMetadata] = None
    
    class Config:
        frozen = True  # Events are immutable
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.aggregate_id),
            "aggregate_type": self.aggregate_type,
            "user_id": str(self.user_id),
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "data": self.data,
            "metadata": self.metadata.dict() if self.metadata else None,
        }
