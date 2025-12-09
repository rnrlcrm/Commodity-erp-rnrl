"""
Authentication Schemas for Mobile OTP Flow

Mobile-first authentication before partner onboarding
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from backend.modules.common.schemas.auth import SendOTPRequest, VerifyOTPRequest, OTPResponse


class CompleteProfileRequest(BaseModel):
    """Complete user profile for new users"""
    full_name: str = Field(..., min_length=2, max_length=200)
    email: Optional[EmailStr] = None


class AuthTokenResponse(BaseModel):
    """JWT token response after successful verification"""
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[UUID] = None  # None for new users who haven't completed onboarding
    mobile_number: str
    is_new_user: bool
    profile_complete: bool
    next_step: str  # "complete_profile" or "start_onboarding" or "dashboard"


class UserProfileResponse(BaseModel):
    """User profile information"""
    id: UUID
    mobile_number: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str
    is_active: bool
    profile_complete: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
