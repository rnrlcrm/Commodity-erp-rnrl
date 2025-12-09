from __future__ import annotations

from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.modules.common.schemas.auth import TokenResponse, SendOTPRequest, VerifyOTPRequest, OTPResponse

# Regex pattern constants
DIGIT_PATTERN = r'^\d+$'
PHONE_PATTERN = r'^\+[1-9]\d{1,14}$'
UPPERCASE_PATTERN = r'[A-Z]'
LOWERCASE_PATTERN = r'[a-z]'
DIGIT_CHECK_PATTERN = r'\d'

# Password policy constants
PASSWORD_DESCRIPTION = "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number"
PASSWORD_MIN_LENGTH_ERROR = "Password must be at least 8 characters long"
PASSWORD_UPPERCASE_ERROR = "Password must contain at least one uppercase letter"
PASSWORD_LOWERCASE_ERROR = "Password must contain at least one lowercase letter"
PASSWORD_NUMBER_ERROR = "Password must contain at least one number"


class SignupRequest(BaseModel):
	email: EmailStr
	password: str = Field(
		min_length=8,
		max_length=128,
		description=PASSWORD_DESCRIPTION
	)
	full_name: Optional[str] = None

	@field_validator('password')
	@classmethod
	def validate_password_strength(cls, v: str) -> str:
		"""Enforce password policy: min 8 chars, 1 uppercase, 1 lowercase, 1 number."""
		if len(v) < 8:
			raise ValueError(PASSWORD_MIN_LENGTH_ERROR)
		if not re.search(UPPERCASE_PATTERN, v):
			raise ValueError(PASSWORD_UPPERCASE_ERROR)
		if not re.search(LOWERCASE_PATTERN, v):
			raise ValueError(PASSWORD_LOWERCASE_ERROR)
		if not re.search(DIGIT_CHECK_PATTERN, v):
			raise ValueError(PASSWORD_NUMBER_ERROR)
		return v


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
	id: str
	email: EmailStr
	full_name: Optional[str] = None
	organization_id: str
	is_active: bool
	parent_user_id: Optional[str] = None
	role: Optional[str] = None
	created_at: datetime
	updated_at: datetime

	class Config:
		from_attributes = True


class CreateSubUserRequest(BaseModel):
	"""Request to create a sub-user (EXTERNAL user under business partner)."""
	mobile_number: str = Field(
		pattern=PHONE_PATTERN,
		description="Mobile number in E.164 format (e.g., +919876543210)"
	)
	full_name: str
	pin: Optional[str] = Field(None, min_length=4, max_length=6, pattern=DIGIT_PATTERN)
	role: Optional[str] = None


class SubUserOut(BaseModel):
	"""Sub-user response."""
	id: str
	mobile_number: str
	full_name: Optional[str]
	role: Optional[str]
	is_active: bool
	parent_user_id: str
	business_partner_id: str
	created_at: datetime
	updated_at: datetime

	class Config:
		from_attributes = True


class Setup2FARequest(BaseModel):
	"""Request to setup or update 2FA PIN."""
	pin: str = Field(min_length=4, max_length=6, pattern=DIGIT_PATTERN)


class Verify2FARequest(BaseModel):
	"""Request to verify 2FA PIN during login."""
	email: EmailStr
	pin: str = Field(min_length=4, max_length=6, pattern=DIGIT_PATTERN)


class TwoFAStatusResponse(BaseModel):
	"""Response for 2FA status."""
	two_fa_enabled: bool
	message: str


class LoginWith2FAResponse(BaseModel):
	"""Response when 2FA is enabled - requires PIN verification."""
	two_fa_required: bool
	message: str
	email: EmailStr


class InternalUserSignupRequest(BaseModel):
	"""Signup request for INTERNAL users (backoffice) with password policy."""
	email: EmailStr
	password: str = Field(
		min_length=8,
		max_length=128,
		description=PASSWORD_DESCRIPTION
	)
	full_name: Optional[str] = None

	@field_validator('password')
	@classmethod
	def validate_password_strength(cls, v: str) -> str:
		"""Enforce password policy for INTERNAL users: min 8 chars, 1 uppercase, 1 lowercase, 1 number."""
		if len(v) < 8:
			raise ValueError(PASSWORD_MIN_LENGTH_ERROR)
		if not re.search(UPPERCASE_PATTERN, v):
			raise ValueError(PASSWORD_UPPERCASE_ERROR)
		if not re.search(LOWERCASE_PATTERN, v):
			raise ValueError(PASSWORD_LOWERCASE_ERROR)
		if not re.search(DIGIT_CHECK_PATTERN, v):
			raise ValueError(PASSWORD_NUMBER_ERROR)
		return v


class ChangePasswordRequest(BaseModel):
	"""Request to change password for INTERNAL users."""
	old_password: str
	new_password: str = Field(
		min_length=8,
		max_length=128,
		description=PASSWORD_DESCRIPTION
	)

	@field_validator('new_password')
	@classmethod
	def validate_password_strength(cls, v: str) -> str:
		"""Enforce password policy for INTERNAL users."""
		if len(v) < 8:
			raise ValueError(PASSWORD_MIN_LENGTH_ERROR)
		if not re.search(UPPERCASE_PATTERN, v):
			raise ValueError(PASSWORD_UPPERCASE_ERROR)
		if not re.search(LOWERCASE_PATTERN, v):
			raise ValueError(PASSWORD_LOWERCASE_ERROR)
		if not re.search(DIGIT_CHECK_PATTERN, v):
			raise ValueError(PASSWORD_NUMBER_ERROR)
		return v
