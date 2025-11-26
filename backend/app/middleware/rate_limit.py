"""
Rate Limiting Middleware

Protects API from abuse using slowapi (Flask-Limiter for FastAPI).

Features:
- Per-IP rate limiting
- Per-user rate limiting
- Different limits per endpoint
- Redis backend for distributed rate limiting
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import Request
from typing import Optional
import os


def get_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    
    Priority:
    1. User ID (if authenticated)
    2. IP address (if not authenticated)
    """
    # Try to get user_id from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize limiter
# Disable rate limiting in test environment
is_test = os.getenv("TESTING", "false").lower() == "true"

limiter = Limiter(
    key_func=get_identifier,
    default_limits=[] if is_test else ["1000/hour", "10000/day"],  # Global default
    storage_uri=os.getenv("REDIS_URL", "memory://"),  # Use Redis in production
    strategy="fixed-window",  # Can be changed to "moving-window" for better accuracy
    enabled=not is_test,  # Disable in tests
)


def setup_rate_limiting(app):
    """
    Setup rate limiting for FastAPI app.
    
    Usage:
        from backend.app.middleware.rate_limit import setup_rate_limiting
        
        app = FastAPI()
        setup_rate_limiting(app)
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter


# Pre-configured rate limit decorators for common use cases
def rate_limit_strict(limit: str = "10/minute"):
    """
    Strict rate limit for sensitive endpoints.
    
    Usage:
        @router.post("/login")
        @rate_limit_strict("5/minute")
        async def login(...):
            pass
    """
    return limiter.limit(limit)


def rate_limit_moderate(limit: str = "100/minute"):
    """
    Moderate rate limit for standard API endpoints.
    
    Usage:
        @router.get("/users")
        @rate_limit_moderate()
        async def list_users(...):
            pass
    """
    return limiter.limit(limit)


def rate_limit_relaxed(limit: str = "1000/minute"):
    """
    Relaxed rate limit for high-frequency endpoints.
    
    Usage:
        @router.get("/health")
        @rate_limit_relaxed()
        async def health_check():
            pass
    """
    return limiter.limit(limit)
