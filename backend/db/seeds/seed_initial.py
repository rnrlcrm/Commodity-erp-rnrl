from __future__ import annotations

import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

try:
    # When running with PYTHONPATH=., we can import as a package-less module
    from backend.modules.settings.services.settings_services import SeedService  # type: ignore
except ModuleNotFoundError:  # Fallback when launched from backend working dir
    from modules.settings.services.settings_services import SeedService  # type: ignore


async def main() -> None:
    database_url = os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+asyncpg://")
    org_name = os.getenv("DEFAULT_ORG_NAME", "Cotton Corp")
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")

    engine = create_async_engine(database_url, future=True)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        service = SeedService(session)
        await service.seed_defaults(org_name, admin_email, admin_password)
        await session.commit()
        print("Seed completed: org, permissions, role, admin user")


if __name__ == "__main__":
    asyncio.run(main())
