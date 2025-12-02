"""Shared response models used across modules."""

from __future__ import annotations

from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response used across all API endpoints."""
    
    detail: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code", alias="error_code")
    field: Optional[str] = Field(None, description="Field name if validation error")
    
    # Alternative fields for compatibility with risk module
    error: Optional[str] = Field(None, description="Error type (alternative to code)")
    message: Optional[str] = Field(None, description="Error message (alternative to detail)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        populate_by_name = True  # Allow both 'code' and 'error_code'
