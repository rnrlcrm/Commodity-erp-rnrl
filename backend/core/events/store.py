"""
Event Store

Persists events to database with JSONB for flexibility.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.session import Base


class Event(Base):
    """Event storage table - stores ALL events from ALL modules"""
    
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"), index=True)
    version = Column(Integer, nullable=False, default=1)
    data = Column(JSONB, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class EventStore:
    """
    Repository for storing and retrieving events.
    
    Provides methods to:
    - Store new events
    - Query events by aggregate
    - Query events by type
    - Query events by user
    - Query events by time range
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def append(
        self,
        event_type: str,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        user_id: uuid.UUID,
        data: dict,
        metadata: Optional[dict] = None,
        version: int = 1,
    ) -> Event:
        """
        Append a new event to the store.
        
        Events are immutable once written.
        """
        event = Event(
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            user_id=user_id,
            data=data,
            metadata=metadata,
            version=version,
        )
        
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        
        return event
    
    async def get_by_aggregate(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: Optional[str] = None,
    ) -> List[Event]:
        """Get all events for a specific aggregate (entity)"""
        query = select(Event).where(Event.aggregate_id == aggregate_id)
        
        if aggregate_type:
            query = query.where(Event.aggregate_type == aggregate_type)
        
        query = query.order_by(Event.timestamp.asc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_type(
        self,
        event_type: str,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get events by type"""
        query = select(Event).where(Event.event_type == event_type)
        query = query.order_by(Event.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get all events triggered by a specific user"""
        query = select(Event).where(Event.user_id == user_id)
        query = query.order_by(Event.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        aggregate_type: Optional[str] = None,
    ) -> List[Event]:
        """Get events within a time range"""
        query = select(Event).where(Event.timestamp >= start_time)
        
        if end_time:
            query = query.where(Event.timestamp <= end_time)
        
        if aggregate_type:
            query = query.where(Event.aggregate_type == aggregate_type)
        
        query = query.order_by(Event.timestamp.asc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_by_aggregate(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: Optional[str] = None,
    ) -> int:
        """Count events for an aggregate"""
        query = select(Event).where(Event.aggregate_id == aggregate_id)
        
        if aggregate_type:
            query = query.where(Event.aggregate_type == aggregate_type)
        
        result = await self.session.execute(query)
        return len(result.scalars().all())
