"""
Audit Trail API

Provides endpoints for querying event history and audit trails.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.events.audit import AuditEntry, AuditService
from backend.db.session import get_db

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/entity/{entity_id}", response_model=List[AuditEntry])
async def get_entity_history(
    entity_id: UUID,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete change history for an entity.
    
    Example: Get all changes to Organization with ID xyz
    """
    audit = AuditService(db)
    return await audit.get_entity_history(entity_id, entity_type)


@router.get("/user/{user_id}", response_model=List[AuditEntry])
async def get_user_activity(
    user_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all actions performed by a specific user.
    
    Example: Show what User X did today
    """
    audit = AuditService(db)
    return await audit.get_user_activity(user_id, limit)


@router.get("/recent", response_model=List[AuditEntry])
async def get_recent_changes(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    hours: int = Query(24, ge=1, le=168, description="Look back hours"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent changes across the system.
    
    Example: Show all commodity changes in last 24 hours
    """
    audit = AuditService(db)
    return await audit.get_recent_changes(entity_type, hours)


@router.get("/count/{entity_id}")
async def get_change_count(
    entity_id: UUID,
    entity_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Get total number of changes to an entity.
    
    Returns: {"count": 42}
    """
    audit = AuditService(db)
    count = await audit.get_change_count(entity_id, entity_type)
    return {"count": count}
