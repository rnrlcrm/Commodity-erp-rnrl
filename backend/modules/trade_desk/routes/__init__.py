"""
Trade Desk REST API Routes

Re-exports routers from availability_routes.py and requirement_routes.py
"""

from backend.modules.trade_desk.routes.availability_routes import (
    router as availability_router,
)
from backend.modules.trade_desk.routes.requirement_routes import (
    router as requirement_router,
)

# For backward compatibility, export availability router as default
router = availability_router

__all__ = ["router", "availability_router", "requirement_router"]
