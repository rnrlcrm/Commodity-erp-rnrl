"""
Application-wide dependencies

Provides dependency injection for common services.
"""

from typing import AsyncGenerator

import redis.asyncio as redis

from backend.core.settings.config import settings


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Get Redis client dependency
    
    Used by:
    - WebSocket manager (pub/sub)
    - Session management
    - Rate limiting
    - OTP storage
    """
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


__all__ = ["get_redis"]
