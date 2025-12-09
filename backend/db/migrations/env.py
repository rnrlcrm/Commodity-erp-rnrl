from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

# Add repository root to sys.path to allow `import backend.*`
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from backend.db.session import Base  # noqa: E402

# ============================================
# IMPORT ALL MODELS FOR MIGRATION GENERATION
# Total: 58 tables across the system
# ============================================

# Core Models - Events & Outbox (2 tables)
from backend.core.events.store import Event  # noqa: F401,E402
from backend.core.outbox.models import EventOutbox  # noqa: F401,E402

# Core Models - Capabilities (3 tables)
from backend.core.auth.capabilities.models import (  # noqa: F401,E402
    Capability,
    UserCapability,
    RoleCapability,
)

# Core Models - GDPR (4 tables)
from backend.core.gdpr.data_retention import DataRetentionPolicy  # noqa: F401,E402
from backend.core.gdpr.consent import ConsentVersion, UserConsent  # noqa: F401,E402
from backend.core.gdpr.user_rights import UserRightRequest  # noqa: F401,E402

# Settings Models - Users & Auth (6 tables)
from backend.modules.settings.models.settings_models import (  # noqa: F401,E402
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    RefreshToken,
)

# Settings Models - Organization (5 tables)
from backend.modules.settings.organization.models import (  # noqa: F401,E402
    Organization,
    OrganizationGST,
    OrganizationBankAccount,
    OrganizationFinancialYear,
    OrganizationDocumentSeries,
)

# Settings Models - Commodities (11 tables)
from backend.modules.settings.commodities.models import (  # noqa: F401,E402
    Commodity,
    CommodityVariety,
    CommodityParameter,
    SystemCommodityParameter,
    PaymentTerm,
    DeliveryTerm,
    WeightmentTerm,
    PassingTerm,
    BargainType,
    TradeType,
    CommissionStructure,
)
from backend.modules.settings.commodities.hsn_models import (  # noqa: F401,E402
    HSNKnowledgeBase,
)

# Settings Models - Locations (1 table)
from backend.modules.settings.locations.models import Location  # noqa: F401,E402

# Partner Models (9 tables)
from backend.modules.partners.models import (  # noqa: F401,E402
    BusinessPartner,
    PartnerLocation,
    PartnerEmployee,
    PartnerDocument,
    PartnerVehicle,
    PartnerOnboardingApplication,
    PartnerAmendment,
    PartnerKYCRenewal,
    PartnerBranch,
)

# Auth Models (1 table)
from backend.modules.auth.models import UserSession  # noqa: F401,E402

# Notification Models (3 tables)
from backend.modules.notifications.models.notification import (  # noqa: F401,E402
    Notification,
    NotificationPreference,
    DeviceToken,
)

# Trade Desk Models - Import in dependency order to avoid circular references (13 tables)
# Base entities (no FK to other trade_desk tables)
from backend.modules.trade_desk.models.requirement import Requirement  # noqa: F401,E402
from backend.modules.trade_desk.models.availability import Availability  # noqa: F401,E402
from backend.modules.trade_desk.models.match_token import MatchToken  # noqa: F401,E402
from backend.modules.trade_desk.models.requirement_embedding import RequirementEmbedding  # noqa: F401,E402
from backend.modules.trade_desk.models.availability_embedding import AvailabilityEmbedding  # noqa: F401,E402

# Negotiations (depends on match_tokens, requirements, availabilities)
from backend.modules.trade_desk.models.negotiation import Negotiation  # noqa: F401,E402
from backend.modules.trade_desk.models.negotiation_offer import NegotiationOffer  # noqa: F401,E402
from backend.modules.trade_desk.models.negotiation_message import NegotiationMessage  # noqa: F401,E402

# Trades (depends on negotiations)
from backend.modules.trade_desk.models.trade import Trade  # noqa: F401,E402
from backend.modules.trade_desk.models.trade_amendment import TradeAmendment  # noqa: F401,E402
from backend.modules.trade_desk.models.trade_signature import TradeSignature  # noqa: F401,E402

# Match outcomes (depends on trades)
from backend.modules.trade_desk.models.match_outcome import MatchOutcome  # noqa: F401,E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _include_object(object, name, type_, reflected, compare_to):  # noqa: ANN001
    # Avoid re-generating composite unique constraints that are redundant with PK
    if type_ == "unique_constraint" and name in {"uq_role_permission", "uq_user_role"}:
        return False
    return True


def get_database_url() -> str:
    """Get database URL from environment."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback for local development
        db_url = "postgresql+psycopg://commodity_user:commodity_password@localhost:5432/commodity_erp"
    
    # For async migrations, ensure URL uses asyncpg driver
    # For sync operations (like alembic commands), use psycopg
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    # Convert asyncpg to psycopg for offline mode
    if "asyncpg" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=_include_object,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with provided connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=_include_object,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    db_url = get_database_url()
    
    # Ensure async driver for online migrations
    if "postgresql://" in db_url and "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    if "postgresql+psycopg://" in db_url:
        db_url = db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
    
    connectable = create_async_engine(db_url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
