"""
Capability Management Schemas

Request/Response schemas for capability management API.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CapabilityResponse(BaseModel):
    """Capability definition response"""
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    category: str
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCapabilityResponse(BaseModel):
    """User capability assignment response"""
    id: UUID
    user_id: UUID
    capability: CapabilityResponse
    granted_at: datetime
    granted_by: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[UUID] = None
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class RoleCapabilityResponse(BaseModel):
    """Role capability assignment response"""
    id: UUID
    role_id: UUID
    capability: CapabilityResponse
    granted_at: datetime
    granted_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class GrantCapabilityToUserRequest(BaseModel):
    """Request to grant a capability to a user"""
    capability_code: str = Field(..., description="Capability code (e.g., AVAILABILITY_CREATE)")
    expires_at: Optional[datetime] = Field(None, description="When the capability expires")
    reason: Optional[str] = Field(None, description="Reason for granting capability")


class RevokeCapabilityFromUserRequest(BaseModel):
    """Request to revoke a capability from a user"""
    capability_code: str = Field(..., description="Capability code to revoke")
    reason: Optional[str] = Field(None, description="Reason for revoking capability")


class GrantCapabilityToRoleRequest(BaseModel):
    """Request to grant a capability to a role"""
    capability_code: str = Field(..., description="Capability code (e.g., AVAILABILITY_CREATE)")


class UserCapabilitiesResponse(BaseModel):
    """All capabilities for a user"""
    user_id: UUID
    capabilities: List[str] = Field(..., description="List of capability codes")
    direct_capabilities: List[UserCapabilityResponse] = Field(..., description="Directly assigned capabilities")
    role_capabilities: List[RoleCapabilityResponse] = Field(default_factory=list, description="Capabilities from roles")


class CapabilityCheckRequest(BaseModel):
    """Request to check if user has capability"""
    capability_code: str = Field(..., description="Capability code to check")


class CapabilityCheckResponse(BaseModel):
    """Response for capability check"""
    user_id: UUID
    capability_code: str
    has_capability: bool
    granted_via: Optional[str] = Field(None, description="How capability was granted (direct/role)")


class CapabilityListResponse(BaseModel):
    """List of all capabilities"""
    total: int
    capabilities: List[CapabilityResponse]


class CapabilityCategoryFilter(BaseModel):
    """Filter capabilities by category"""
    category: Optional[str] = None
    is_system: Optional[bool] = None
