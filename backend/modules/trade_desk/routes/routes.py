"""
Trade Desk Module Routes Registration

Registers all Trade Desk routers with the main FastAPI application.
Includes:
- Engine 1: Availability Engine
- Engine 2: Requirement Engine (🚀 2035-ready with AI enhancements)
"""

from fastapi import APIRouter

from backend.modules.trade_desk.routes.availability_routes import (
    router as availability_router,
)
from backend.modules.trade_desk.routes.requirement_routes import (
    router as requirement_router,
)

# Create main trade desk router
trade_desk_router = APIRouter(prefix="/trade-desk", tags=["Trade Desk"])

# Include sub-routers
trade_desk_router.include_router(availability_router)
trade_desk_router.include_router(requirement_router)

__all__ = ["trade_desk_router", "availability_router", "requirement_router"]
