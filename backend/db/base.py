"""
Re-export Base from session_module to ensure single Base instance across codebase.
CRITICAL: All models must use the same Base for Alembic autogenerate to work.
"""
from backend.db.session_module import Base

__all__ = ["Base"]
