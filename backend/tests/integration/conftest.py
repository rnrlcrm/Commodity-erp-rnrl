"""
Integration Test Infrastructure with Testcontainers + PostgreSQL

Provides real PostgreSQL database for thorough integration testing of all modules.
"""
import asyncio
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import text, create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from backend.db.session_module import Base


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Session-scoped PostgreSQL container.
    Starts once for all tests, provides real database.
    """
    container = PostgresContainer("postgres:15-alpine")
    container.start()
    
    yield container
    
    container.stop()


@pytest.fixture(scope="session")
def sync_database_url(postgres_container: PostgresContainer) -> str:
    """Synchronous database URL for schema creation."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def async_database_url(postgres_container: PostgresContainer) -> str:
    """Asynchronous database URL for async operations."""
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def setup_database_schema(sync_database_url: str):
    """
    Create all tables in the database using SQLAlchemy models.
    Runs once per test session.
    """
    # Import all models to register them with Base
    from backend.modules.partners.models import (
        BusinessPartner, PartnerLocation, PartnerEmployee,
        PartnerDocument, PartnerVehicle, PartnerOnboardingApplication,
        PartnerAmendment, PartnerKYCRenewal
    )
    from backend.modules.trade_desk.models.requirement import Requirement
    from backend.modules.trade_desk.models.availability import Availability
    from backend.modules.settings.commodities.models import Commodity, PaymentTerm
    from backend.modules.settings.locations.models import Location
    from backend.modules.settings.organization.models import Organization, Branch, Department
    from backend.modules.settings.models.settings_models import User
    
    # Create sync engine
    engine = create_engine(sync_database_url, poolclass=NullPool)
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        yield
    finally:
        # Cleanup
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(
    async_database_url: str,
    setup_database_schema,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session for each test.
    Each test gets a clean transaction that rolls back.
    """
    engine = create_async_engine(async_database_url, poolclass=NullPool, echo=False)
    
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Start transaction
        async with session.begin():
            yield session
            # Rollback happens automatically when exiting context
    
    await engine.dispose()


@pytest_asyncio.fixture
async def seed_organization(db_session: AsyncSession):
    """Create main organization for testing."""
    from backend.modules.settings.organization.models import Organization
    
    org = Organization(
        id=uuid.uuid4(),
        legal_name="Main Company Ltd",
        trade_name="Main Company",
        country="India",
        tax_id_number="27AAAAA0000A1Z5",
        status="active"
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def seed_locations(db_session: AsyncSession):
    """Create test locations."""
    from backend.modules.settings.locations.models import Location
    
    locations = [
        Location(
            id=uuid.uuid4(),
            name="Mumbai",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            location_type="city"
        ),
        Location(
            id=uuid.uuid4(),
            name="Delhi",
            city="Delhi",
            state="Delhi",
            country="India",
            location_type="city"
        ),
        Location(
            id=uuid.uuid4(),
            name="Bangalore",
            city="Bangalore",
            state="Karnataka",
            country="India",
            location_type="city"
        ),
    ]
    
    for loc in locations:
        db_session.add(loc)
    
    await db_session.flush()
    return locations


@pytest_asyncio.fixture
async def seed_commodities(db_session: AsyncSession):
    """Create test commodities."""
    from backend.modules.settings.commodities.models import Commodity
    
    commodities = [
        Commodity(
            id=uuid.uuid4(),
            name="Cotton",
            commodity_type="agricultural",
            base_unit="kg",
            status="active"
        ),
        Commodity(
            id=uuid.uuid4(),
            name="Gold",
            commodity_type="precious_metal",
            base_unit="gram",
            status="active"
        ),
    ]
    
    for comm in commodities:
        db_session.add(comm)
    
    await db_session.flush()
    return commodities


@pytest_asyncio.fixture
async def seed_payment_terms(db_session: AsyncSession):
    """Create test payment terms."""
    from backend.modules.settings.commodities.models import PaymentTerm
    
    terms = [
        PaymentTerm(
            id=uuid.uuid4(),
            name="Immediate",
            days=0,
            status="active"
        ),
        PaymentTerm(
            id=uuid.uuid4(),
            name="Net 30",
            days=30,
            status="active"
        ),
    ]
    
    for term in terms:
        db_session.add(term)
    
    await db_session.flush()
    return terms
