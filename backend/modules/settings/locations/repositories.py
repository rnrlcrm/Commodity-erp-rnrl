"""
Location Module Repository

Data access layer for Location model.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.locations.models import Location


class LocationRepository:
    """Repository for Location database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, location: Location) -> Location:
        """Create a new location"""
        self.db.add(location)
        await self.db.flush()
        await self.db.refresh(location)
        return location
    
    async def get_by_id(self, location_id: UUID) -> Optional[Location]:
        """Get location by ID"""
        result = await self.db.execute(
            select(Location).where(Location.id == location_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_google_place_id(self, place_id: str) -> Optional[Location]:
        """Get location by Google Place ID (prevents duplicates)"""
        result = await self.db.execute(
            select(Location).where(Location.google_place_id == place_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        region: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Location], int]:
        """
        List locations with optional filters.
        
        Returns:
            Tuple of (locations list, total count)
        """
        from sqlalchemy import func
        
        query = select(Location)
        
        # Apply filters
        if city:
            query = query.where(Location.city.ilike(f"%{city}%"))
        
        if state:
            query = query.where(Location.state.ilike(f"%{state}%"))
        
        if region:
            query = query.where(Location.region == region)
        
        if is_active is not None:
            query = query.where(Location.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Location.name.ilike(search_pattern),
                    Location.city.ilike(search_pattern),
                    Location.state.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(Location)
        if city:
            count_query = count_query.where(Location.city.ilike(f"%{city}%"))
        if state:
            count_query = count_query.where(Location.state.ilike(f"%{state}%"))
        if region:
            count_query = count_query.where(Location.region == region)
        if is_active is not None:
            count_query = count_query.where(Location.is_active == is_active)
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Location.name.ilike(search_pattern),
                    Location.city.ilike(search_pattern),
                    Location.state.ilike(search_pattern)
                )
            )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        query = query.order_by(Location.name).offset(offset).limit(limit)
        result = await self.db.execute(query)
        locations = list(result.scalars().all())
        
        return locations, total
    
    async def update(self, location: Location) -> Location:
        """Update an existing location"""
        await self.db.flush()
        await self.db.refresh(location)
        return location
    
    async def soft_delete(self, location: Location) -> Location:
        """Soft delete a location (set is_active=False)"""
        location.is_active = False
        return await self.update(location)
    
    async def count_references(self, location_id: UUID) -> int:
        """
        Count how many other entities reference this location.
        Used to prevent deletion of locations in use.
        
        Checks:
        - organizations.location_id (when implemented)
        - users.business_location_id (when implemented)
        - buyers.location_id (TODO: when buyers module is built)
        - sellers.location_id (TODO: when sellers module is built) 
        - trades.loading_location_id (TODO: when trades module is built)
        - trades.delivery_location_id (TODO: when trades module is built)
        """
        from sqlalchemy import func
        from backend.modules.settings.organization.models import Organization
        from backend.modules.settings.models.settings_models import User
        
        count = 0
        
        # Check organizations table (if location_id column exists)
        # TODO: Uncomment when organizations.location_id is added
        # count += self.db.query(Organization).filter(
        #     Organization.location_id == location_id
        # ).count()
        
        # Check users table (if business_location_id column exists)
        # TODO: Uncomment when users.business_location_id is added
        # count += self.db.query(User).filter(
        #     User.business_location_id == location_id
        # ).count()
        
        # TODO: Add checks for buyers table when module is created
        # from backend.modules.buyers.models import Buyer
        # count += self.db.query(Buyer).filter(
        #     Buyer.location_id == location_id
        # ).count()
        
        # TODO: Add checks for sellers table when module is created
        # from backend.modules.sellers.models import Seller
        # count += self.db.query(Seller).filter(
        #     Seller.location_id == location_id
        # ).count()
        
        # TODO: Add checks for trades table when module is created
        # from backend.modules.trades.models import Trade
        # count += self.db.query(Trade).filter(
        #     or_(
        #         Trade.loading_location_id == location_id,
        #         Trade.delivery_location_id == location_id
        #     )
        # ).count()
        
        return count
