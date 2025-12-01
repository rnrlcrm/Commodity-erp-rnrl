"""
EOD (End of Day) Expiry Cron Job

Automatically expires availabilities and requirements past their EOD cutoff time.

DESIGN:
- Timezone-aware expiry (respects location.timezone)
- Runs every hour via APScheduler
- Updates status: ACTIVE → EXPIRED
- Emits events for notifications

WORKFLOW:
1. Find availabilities/requirements with eod_cutoff <= NOW() (UTC)
2. Join with settings_locations to get timezone
3. Calculate timezone-adjusted EOD (midnight in that timezone)
4. Update status to EXPIRED
5. Emit 'availability.expired' or 'requirement.expired' event

TIMEZONE SUPPORT:
- Mumbai (Asia/Kolkata): EOD = 11:59 PM IST
- New York (America/New_York): EOD = 11:59 PM EST
- London (Europe/London): EOD = 11:59 PM GMT
- All stored as UTC timestamps in database
"""

import logging
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import pytz
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.modules.trade_desk.models.availability import Availability
from backend.modules.trade_desk.models.requirement import Requirement
from backend.modules.trade_desk.enums import AvailabilityStatus, RequirementStatus
from backend.modules.settings.locations.models import Location
from backend.core.database import get_async_session

logger = logging.getLogger(__name__)


class EODExpiryJob:
    """
    End of Day expiry management with timezone awareness.
    
    Automatically expires positions past their EOD cutoff.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize EOD expiry job.
        
        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
    
    async def expire_availabilities(self) -> int:
        """
        Expire availabilities past their EOD cutoff.
        
        Returns:
            Number of availabilities expired
        """
        now_utc = datetime.now(timezone.utc)
        
        # Query availabilities with eod_cutoff <= now_utc
        # Status must be ACTIVE or AVAILABLE (not already EXPIRED/SOLD/CANCELLED)
        query = (
            select(Availability)
            .options(selectinload(Availability.location))
            .where(
                and_(
                    Availability.status.in_([
                        AvailabilityStatus.ACTIVE.value,
                        AvailabilityStatus.AVAILABLE.value,
                        AvailabilityStatus.PARTIALLY_SOLD.value
                    ]),
                    Availability.eod_cutoff <= now_utc
                )
            )
        )
        
        result = await self.db.execute(query)
        availabilities = result.scalars().all()
        
        expired_count = 0
        
        for availability in availabilities:
            # Log expiry with timezone info
            location_tz = "UTC"
            if availability.location and availability.location.timezone:
                location_tz = availability.location.timezone
            
            logger.info(
                f"Expiring availability {availability.id}: "
                f"EOD cutoff {availability.eod_cutoff} (location timezone: {location_tz})"
            )
            
            # Update status to EXPIRED
            availability.status = AvailabilityStatus.EXPIRED.value
            availability.updated_at = now_utc
            
            # Emit event (will be handled by event bus)
            await self._emit_availability_expired_event(availability.id)
            
            expired_count += 1
        
        # Commit all updates
        await self.db.commit()
        
        logger.info(f"Expired {expired_count} availabilities at {now_utc}")
        
        return expired_count
    
    async def expire_requirements(self) -> int:
        """
        Expire requirements past their EOD cutoff.
        
        Returns:
            Number of requirements expired
        """
        now_utc = datetime.now(timezone.utc)
        
        # Query requirements with eod_cutoff <= now_utc
        # Status must be ACTIVE or PENDING_APPROVAL (not already EXPIRED/FULFILLED/CANCELLED)
        query = (
            select(Requirement)
            .where(
                and_(
                    Requirement.status.in_([
                        RequirementStatus.ACTIVE.value,
                        RequirementStatus.PENDING_APPROVAL.value,
                        RequirementStatus.PARTIALLY_FULFILLED.value
                    ]),
                    Requirement.eod_cutoff <= now_utc
                )
            )
        )
        
        result = await self.db.execute(query)
        requirements = result.scalars().all()
        
        expired_count = 0
        
        for requirement in requirements:
            # Note: Requirements don't have location directly, they have delivery_locations JSONB
            # EOD cutoff is already pre-calculated and stored in UTC
            
            logger.info(
                f"Expiring requirement {requirement.id}: "
                f"EOD cutoff {requirement.eod_cutoff}"
            )
            
            # Update status to EXPIRED
            requirement.status = RequirementStatus.EXPIRED.value
            requirement.updated_at = now_utc
            
            # Emit event (will be handled by event bus)
            await self._emit_requirement_expired_event(requirement.id)
            
            expired_count += 1
        
        # Commit all updates
        await self.db.commit()
        
        logger.info(f"Expired {expired_count} requirements at {now_utc}")
        
        return expired_count
    
    async def run_eod_expiry(self) -> dict:
        """
        Run EOD expiry for both availabilities and requirements.
        
        This is the main entry point for the cron job.
        
        Returns:
            Dictionary with expiry counts
        """
        logger.info("Starting EOD expiry job...")
        
        start_time = datetime.now(timezone.utc)
        
        # Expire availabilities
        availabilities_expired = await self.expire_availabilities()
        
        # Expire requirements
        requirements_expired = await self.expire_requirements()
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "availabilities_expired": availabilities_expired,
            "requirements_expired": requirements_expired,
            "total_expired": availabilities_expired + requirements_expired
        }
        
        logger.info(
            f"EOD expiry job completed: "
            f"{availabilities_expired} availabilities, "
            f"{requirements_expired} requirements expired "
            f"in {duration:.2f}s"
        )
        
        return result
    
    async def _emit_availability_expired_event(self, availability_id: UUID) -> None:
        """
        Emit availability.expired event.
        
        Args:
            availability_id: Availability UUID
        """
        # TODO: Integrate with event bus
        # For now, just log
        logger.info(f"Event: availability.expired - {availability_id}")
        
        # When event bus is integrated:
        # await event_bus.emit('availability.expired', {
        #     'availability_id': str(availability_id),
        #     'expired_at': datetime.now(timezone.utc).isoformat(),
        #     'reason': 'EOD_CUTOFF'
        # })
    
    async def _emit_requirement_expired_event(self, requirement_id: UUID) -> None:
        """
        Emit requirement.expired event.
        
        Args:
            requirement_id: Requirement UUID
        """
        # TODO: Integrate with event bus
        # For now, just log
        logger.info(f"Event: requirement.expired - {requirement_id}")
        
        # When event bus is integrated:
        # await event_bus.emit('requirement.expired', {
        #     'requirement_id': str(requirement_id),
        #     'expired_at': datetime.now(timezone.utc).isoformat(),
        #     'reason': 'EOD_CUTOFF'
        # })


# ========================================================================
# SCHEDULER CONFIGURATION
# ========================================================================

async def run_eod_expiry_job():
    """
    Standalone function to run EOD expiry job.
    
    This can be called by:
    1. APScheduler (recommended)
    2. Celery task
    3. Manual trigger via admin endpoint
    
    Usage with APScheduler:
    ```python
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from backend.modules.trade_desk.cron.eod_expiry import run_eod_expiry_job
    
    scheduler = AsyncIOScheduler()
    
    # Run every hour
    scheduler.add_job(
        run_eod_expiry_job,
        'cron',
        hour='*',  # Every hour
        minute=5,  # At 5 minutes past the hour
        id='eod_expiry',
        replace_existing=True
    )
    
    scheduler.start()
    ```
    """
    async for db in get_async_session():
        try:
            eod_job = EODExpiryJob(db)
            result = await eod_job.run_eod_expiry()
            logger.info(f"EOD expiry job result: {result}")
            return result
        except Exception as e:
            logger.error(f"EOD expiry job failed: {e}", exc_info=True)
            raise
        finally:
            await db.close()


# ========================================================================
# TIMEZONE UTILITIES
# ========================================================================

def calculate_eod_cutoff(location_timezone: str) -> datetime:
    """
    Calculate EOD cutoff for given timezone.
    
    Always returns midnight (00:00) of NEXT day in that timezone,
    converted to UTC for storage.
    
    Args:
        location_timezone: Timezone string (e.g., 'Asia/Kolkata', 'America/New_York')
    
    Returns:
        EOD cutoff as UTC datetime
    
    Examples:
        >>> # Mumbai location
        >>> calculate_eod_cutoff('Asia/Kolkata')
        datetime.datetime(2025, 12, 2, 18, 30, 0, tzinfo=UTC)  # Next day midnight IST in UTC
        
        >>> # New York location
        >>> calculate_eod_cutoff('America/New_York')
        datetime.datetime(2025, 12, 2, 5, 0, 0, tzinfo=UTC)  # Next day midnight EST in UTC
    """
    try:
        tz = pytz.timezone(location_timezone)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"Unknown timezone: {location_timezone}, using UTC")
        tz = pytz.UTC
    
    # Get current time in that timezone
    now_in_tz = datetime.now(tz)
    
    # Next midnight in that timezone (00:00 of next day)
    from datetime import timedelta
    next_midnight = (now_in_tz + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    # Convert to UTC for storage
    return next_midnight.astimezone(pytz.UTC)


def get_location_eod_cutoff(location: Location) -> datetime:
    """
    Get EOD cutoff for a specific location.
    
    Args:
        location: Location model instance
    
    Returns:
        EOD cutoff as UTC datetime
    """
    location_tz = location.timezone if location.timezone else "UTC"
    return calculate_eod_cutoff(location_tz)
