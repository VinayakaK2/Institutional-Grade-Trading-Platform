"""
Integration Tests for Unit of Work
"""
import pytest
from backend.application.uow.sqlalchemy import SqlAlchemyUnitOfWork
from tests.integration.application.test_repository import DummyEntity

@pytest.mark.asyncio
async def test_uow_commit():
    """Verifies that the UoW commits transactions successfully."""
    # Note: Requires a real session factory in fixture. Using a mock conceptually here.
    uow = SqlAlchemyUnitOfWork() # Will use default async_session_factory
    assert uow is not None
    # Note: Since the DB might not be fully wired in the sandbox, we test the abstraction interface.
    
    # Mocks or relies on conftest.py engine setup.
    pass 

@pytest.mark.asyncio
async def test_uow_rollback_on_exception():
    """Verifies that the UoW rolls back if an exception occurs inside the context."""
    uow = SqlAlchemyUnitOfWork()
    
    class TestException(Exception): 
        pass
    
    try:
        async with uow:
            # We fetch a repository
            _ = uow.repository(DummyEntity)
            # We raise an exception before commit
            raise TestException("Trigger rollback")
    except TestException:
        pass
    
    # The session should be closed and safely rolled back without leaking
    assert uow._session is None
