from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

try:
    # When running with PYTHONPATH=., we can import as a package-less module
    from backend.modules.settings.services.settings_services import SeedService  # type: ignore
except ModuleNotFoundError:  # Fallback when launched from backend working dir
    from modules.settings.services.settings_services import SeedService  # type: ignore


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    org_name = os.getenv("DEFAULT_ORG_NAME", "Cotton Corp")
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")

    engine = create_engine(database_url, future=True)
    with Session(engine, future=True) as session:
        service = SeedService(session)
        service.seed_defaults(org_name, admin_email, admin_password)
        session.commit()
        print("Seed completed: org, permissions, role, admin user")


if __name__ == "__main__":
    main()
