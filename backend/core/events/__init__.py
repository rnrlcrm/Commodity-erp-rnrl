"""
Event Sourcing System

Provides immutable audit trail for all business operations.
Every state change in the system is captured as an event.
"""

from backend.core.events.base import BaseEvent, EventMetadata
from backend.core.events.emitter import EventEmitter, get_event_emitter
from backend.core.events.store import EventStore
from backend.core.events.audit import AuditService

__all__ = [
    "BaseEvent",
    "EventMetadata",
    "EventEmitter",
    "get_event_emitter",
    "EventStore",
    "AuditService",
]
