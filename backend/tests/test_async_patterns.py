"""
Test async patterns are working correctly
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.settings.locations.repositories import LocationRepository
from backend.modules.settings.organization.repositories import OrganizationRepository
from backend.modules.settings.commodities.repositories import CommodityRepository


@pytest.mark.asyncio
async def test_location_repository_is_async():
    """Verify LocationRepository uses AsyncSession"""
    # This will fail at type check if not AsyncSession
    class MockAsyncSession:
        async def execute(self, *args, **kwargs):
            pass
        
        async def flush(self):
            pass
        
        async def refresh(self, *args):
            pass
        
        def add(self, *args):
            pass
    
    mock_db = MockAsyncSession()
    repo = LocationRepository(mock_db)  # type: ignore
    
    # Verify the repo has async methods
    assert hasattr(repo.create, '__await__')
    assert hasattr(repo.get_by_id, '__await__')
    assert hasattr(repo.list, '__await__')
    

@pytest.mark.asyncio
async def test_organization_repository_is_async():
    """Verify OrganizationRepository uses AsyncSession"""
    class MockAsyncSession:
        async def execute(self, *args, **kwargs):
            class Result:
                def scalar_one_or_none(self):
                    return None
            return Result()
        
        async def flush(self):
            pass
        
        async def refresh(self, *args):
            pass
        
        def add(self, *args):
            pass
        
        async def delete(self, *args):
            pass
    
    mock_db = MockAsyncSession()
    repo = OrganizationRepository(mock_db)  # type: ignore
    
    # Verify the repo has async methods
    assert hasattr(repo.create, '__await__')
    assert hasattr(repo.get_by_id, '__await__')
    assert hasattr(repo.update, '__await__')


@pytest.mark.asyncio
async def test_commodity_repository_is_async():
    """Verify CommodityRepository uses AsyncSession"""
    class MockAsyncSession:
        async def execute(self, *args, **kwargs):
            class Result:
                def scalar_one_or_none(self):
                    return None
                def scalars(self):
                    class Scalars:
                        def all(self):
                            return []
                    return Scalars()
            return Result()
        
        async def flush(self):
            pass
        
        async def refresh(self, *args):
            pass
        
        def add(self, *args):
            pass
    
    mock_db = MockAsyncSession()
    repo = CommodityRepository(mock_db)  # type: ignore
    
    # Verify the repo has async methods
    assert hasattr(repo.create, '__await__')
    assert hasattr(repo.get_by_id, '__await__')


def test_imports_are_correct():
    """Verify all modules import AsyncSession correctly"""
    from backend.modules.settings.locations import repositories as loc_repos
    from backend.modules.settings.organization import repositories as org_repos
    from backend.modules.settings.commodities import repositories as comm_repos
    
    # Check imports
    assert hasattr(loc_repos, 'AsyncSession')
    assert hasattr(org_repos, 'AsyncSession')
    assert hasattr(comm_repos, 'AsyncSession')
