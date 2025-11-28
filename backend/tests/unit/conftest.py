"""
Pytest configuration for CDPS unit tests

Provides fixtures for database sessions and test data.
"""

import pytest

# CRITICAL: Register SQLite-compatible compilers BEFORE importing any models
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateColumn
from sqlalchemy.sql.expression import TextClause
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import ARRAY

# Patch ARRAY type for SQLite (store as JSON TEXT)
class ARRAYSQLite(TypeDecorator):
    """SQLite-compatible ARRAY - stores as JSON TEXT"""
    impl = TEXT
    cache_ok = True

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    """Compile ARRAY as TEXT for SQLite"""
    return "TEXT"

# Patch server_default NOW() to CURRENT_TIMESTAMP for SQLite
@compiles(CreateColumn, "sqlite")
def compile_column_sqlite(element, compiler, **kw):
    """
    Compile column creation for SQLite.
    Fixes:
    - DEFAULT NOW() → DEFAULT CURRENT_TIMESTAMP
    - DEFAULT '{}'::json → DEFAULT '{}'
    - ARRAY → TEXT
    """
    column = element.element
    
    # Get the standard column spec
    text = compiler.visit_create_column(element, **kw)
    
    # Replace NOW() with CURRENT_TIMESTAMP for SQLite compatibility
    if "NOW()" in text:
        text = text.replace("NOW()", "CURRENT_TIMESTAMP")
    
    # Remove ::json cast (PostgreSQL syntax not supported in SQLite)
    if "::json" in text:
        text = text.replace("::json", "")
    
    return text

# Now import everything else
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db.session import Base
from backend.modules.partners.models import BusinessPartner


# Test database engine (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="function")
def db_session():
    """
    Create sync database session for each test.
    """
    Base.metadata.create_all(bind=test_engine)
    
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
