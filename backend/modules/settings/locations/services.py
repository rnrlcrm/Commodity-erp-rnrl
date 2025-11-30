"""
Location Module Services

Business logic for location management.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.orm import Session

from backend.core.errors.exceptions import BadRequestException, NotFoundException
from backend.core.events.emitter import EventEmitter
from backend.core.outbox import OutboxRepository
from backend.modules.settings.locations.events import (
    LocationCreatedEvent,
    LocationDeletedEvent,
    LocationEventData,
    LocationUpdatedEvent,
)
from backend.modules.settings.locations.google_maps import GoogleMapsService
from backend.modules.settings.locations.models import Location
from backend.modules.settings.locations.repositories import LocationRepository
from backend.modules.settings.locations.schemas import (
    GooglePlaceDetails,
    GooglePlaceSuggestion,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)


# Region mapping based on Indian state codes
STATE_REGION_MAP = {
    # West
    "MH": "WEST",  # Maharashtra
    "GJ": "WEST",  # Gujarat
    "RJ": "WEST",  # Rajasthan
    "GA": "WEST",  # Goa
    
    # South
    "TN": "SOUTH",  # Tamil Nadu
    "KA": "SOUTH",  # Karnataka
    "KL": "SOUTH",  # Kerala
    "AP": "SOUTH",  # Andhra Pradesh
    "TS": "SOUTH",  # Telangana
    "PY": "SOUTH",  # Puducherry
    
    # North
    "PB": "NORTH",  # Punjab
    "HR": "NORTH",  # Haryana
    "UP": "NORTH",  # Uttar Pradesh
    "UK": "NORTH",  # Uttarakhand
    "HP": "NORTH",  # Himachal Pradesh
    "DL": "NORTH",  # Delhi
    "JK": "NORTH",  # Jammu & Kashmir
    "LA": "NORTH",  # Ladakh
    "CH": "NORTH",  # Chandigarh
    
    # Central
    "MP": "CENTRAL",  # Madhya Pradesh
    "CG": "CENTRAL",  # Chhattisgarh
    
    # East
    "WB": "EAST",  # West Bengal
    "OD": "EAST",  # Odisha
    "JH": "EAST",  # Jharkhand
    "BR": "EAST",  # Bihar
    
    # Northeast
    "AS": "NORTHEAST",  # Assam
    "NL": "NORTHEAST",  # Nagaland
    "TR": "NORTHEAST",  # Tripura
    "MZ": "NORTHEAST",  # Mizoram
    "MN": "NORTHEAST",  # Manipur
    "SK": "NORTHEAST",  # Sikkim
    "AR": "NORTHEAST",  # Arunachal Pradesh
    "ML": "NORTHEAST",  # Meghalaya
}


def map_state_to_region(state_code: Optional[str]) -> str:
    """
    Map Indian state code to region.
    
    Args:
        state_code: 2-letter state code (e.g., "MH", "GJ")
        
    Returns:
        Region name (WEST, SOUTH, NORTH, CENTRAL, EAST, NORTHEAST, UNKNOWN)
    """
    if not state_code:
        return "UNKNOWN"
    
    return STATE_REGION_MAP.get(state_code.upper(), "UNKNOWN")


class LocationService:
    """Service for location management"""
    
    def __init__(self, db: AsyncSession, event_emitter: EventEmitter, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.repository = LocationRepository(db)
        self.event_emitter = event_emitter
        self.google_maps = GoogleMapsService()
        self.redis = redis_client
        self.outbox_repo = OutboxRepository(db)
    
    async def search_google_places(self, query: str) -> List[GooglePlaceSuggestion]:
        """
        Search for places using Google Maps Autocomplete API.
        
        Args:
            query: Search query string
            
        Returns:
            List of place suggestions from Google
        """
        if len(query) < 2:
            raise BadRequestException("Search query must be at least 2 characters")
        
        return self.google_maps.search_places(query)
    
    async def fetch_google_place_details(self, place_id: str) -> GooglePlaceDetails:
        """
        Fetch full place details from Google Place Details API.
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Full location details from Google
            
        Raises:
            NotFoundException: If place not found
        """
        details = self.google_maps.fetch_place_details(place_id)
        
        if not details:
            raise NotFoundException(f"Place not found for place_id: {place_id}")
        
        return details
    
    async def create_or_get_location(
        self,
        data: LocationCreate,
        current_user_id: UUID
    ) -> LocationResponse:
        """
        Create a new location or return existing if google_place_id exists.
        This prevents duplicates.
        
        Args:
            data: Location creation data
            current_user_id: ID of user creating the location
            
        Returns:
            LocationResponse (new or existing)
        """
        # Check if location already exists
        existing = await self.repository.get_by_google_place_id(data.google_place_id)
        if existing:
            return LocationResponse.model_validate(existing)
        
        # Fetch details from Google
        google_details = await self.fetch_google_place_details(data.google_place_id)
        
        # Auto-assign region based on state code
        region = map_state_to_region(google_details.state_code)
        
        # Create location
        location = Location(
            name=data.name,
            google_place_id=data.google_place_id,
            address=google_details.formatted_address,
            latitude=google_details.latitude,
            longitude=google_details.longitude,
            pincode=google_details.pincode,
            city=google_details.city,
            district=google_details.district,
            state=google_details.state,
            state_code=google_details.state_code,
            country=google_details.country,
            region=region,
            is_active=True,
            created_by=current_user_id
        )
        
        location = await self.repository.create(location)
        await self.db.flush()
        
        # Emit event
        # Emit event through outbox (transactional)
        await self.outbox_repo.add_event(
            aggregate_id=location.id,
            aggregate_type="Location",
            event_type="LocationCreated",
            payload={
                "location_id": str(location.id),
                "name": location.name,
                "google_place_id": location.google_place_id,
                "city": location.city,
                "state": location.state,
                "region": location.region,
                "is_active": location.is_active,
                "created_by": str(current_user_id)
            },
            topic_name="location-events",
            idempotency_key=None
        )
        
        return LocationResponse.model_validate(location)
    
    async def get_location(self, location_id: UUID) -> LocationResponse:
        """
        Get location by ID.
        
        Args:
            location_id: Location UUID
            
        Returns:
            LocationResponse
            
        Raises:
            NotFoundException: If location not found
        """
        location = await self.repository.get_by_id(location_id)
        
        if not location:
            raise NotFoundException(f"Location not found: {location_id}")
        
        return LocationResponse.model_validate(location)
    
    async def list_locations(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        region: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[LocationResponse], int]:
        """
        List locations with filters.
        
        Returns:
            Tuple of (location list, total count)
        """
        locations, total = await self.repository.list(
            city=city,
            state=state,
            region=region,
            is_active=is_active,
            search=search,
            limit=limit,
            offset=offset
        )
        
        return [LocationResponse.model_validate(loc) for loc in locations], total
    
    async def update_location(
        self,
        location_id: UUID,
        data: LocationUpdate,
        current_user_id: UUID
    ) -> LocationResponse:
        """
        Update location (only name and is_active allowed).
        
        Args:
            location_id: Location UUID
            data: Update data
            current_user_id: ID of user updating
            
        Returns:
            Updated LocationResponse
            
        Raises:
            NotFoundException: If location not found
        """
        location = await self.repository.get_by_id(location_id)
        
        if not location:
            raise NotFoundException(f"Location not found: {location_id}")
        
        # Store old values for event
        old_data = {
            "name": location.name,
            "is_active": location.is_active
        }
        
        # Update allowed fields
        if data.name is not None:
            location.name = data.name
        
        if data.is_active is not None:
            location.is_active = data.is_active
        
        location.updated_by = current_user_id
        location = await self.repository.update(location)
        await self.db.flush()
        
        # Emit event through outbox (transactional)
        changes = {
            "before": old_data,
            "after": {
                "name": location.name,
                "is_active": location.is_active
            }
        }
        
        await self.outbox_repo.add_event(
            aggregate_id=location.id,
            aggregate_type="Location",
            event_type="LocationUpdated",
            payload={
                "location_id": str(location.id),
                "changes": changes,
                "updated_by": str(current_user_id)
            },
            topic_name="location-events",
            idempotency_key=None
        )
        
        return LocationResponse.model_validate(location)
    
    async def delete_location(self, location_id: UUID, current_user_id: UUID) -> dict:
        """
        Soft delete a location (only if not referenced elsewhere).
        
        Args:
            location_id: Location UUID
            current_user_id: ID of user deleting
            
        Returns:
            Success message dict
            
        Raises:
            NotFoundException: If location not found
            BadRequestException: If location is referenced by other entities
        """
        location = await self.repository.get_by_id(location_id)
        
        if not location:
            raise NotFoundException(f"Location not found: {location_id}")
        
        # Check if location is referenced
        ref_count = await self.repository.count_references(location_id)
        if ref_count > 0:
            raise BadRequestException(
                f"Cannot delete location. It is referenced by {ref_count} other entities."
            )
        
        # Soft delete
        location = await self.repository.soft_delete(location)
        location.updated_by = current_user_id
        await self.db.flush()
        
        # Emit event through outbox (transactional)
        await self.outbox_repo.add_event(
            aggregate_id=location.id,
            aggregate_type="Location",
            event_type="LocationDeleted",
            payload={
                "location_id": str(location.id),
                "name": location.name,
                "deleted_by": str(current_user_id)
            },
            topic_name="location-events",
            idempotency_key=None
        )
        
        return {"message": f"Location '{location.name}' deleted successfully"}
