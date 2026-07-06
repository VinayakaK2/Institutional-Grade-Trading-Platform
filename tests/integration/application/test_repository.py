"""
Integration Tests for Generic Repository
"""
import pytest
import pytest_asyncio
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from backend.infrastructure.database.orm.base import Base
from backend.application.repository.sqlalchemy import SqlAlchemyRepository
from backend.domain.shared.primitives import PaginationRequest, SortOptions, SortDirection

class DummyEntity(Base):
    __tablename__ = "dummy_repo_entities"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))


@pytest_asyncio.fixture(scope="function")
async def dummy_repo(db_session, setup_database): # Assumes tests/integration/database/conftest.py fixtures are loaded
    # Register the table explicitly for the test context
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield SqlAlchemyRepository(DummyEntity, db_session)

@pytest.mark.asyncio
async def test_repository_crud(dummy_repo, db_session):
    # Add
    entity = DummyEntity(name="test_crud")
    await dummy_repo.add(entity)
    await db_session.flush()
    assert entity.id is not None
    
    # Get by ID
    fetched = await dummy_repo.get_by_id(entity.id)
    assert fetched is not None
    assert fetched.name == "test_crud"
    
    # Update
    fetched.name = "updated_crud"
    await dummy_repo.update(fetched)
    await db_session.flush()
    updated = await dummy_repo.get_by_id(entity.id)
    assert updated.name == "updated_crud"
    
    # Delete
    await dummy_repo.delete(updated)
    await db_session.flush()
    deleted = await dummy_repo.get_by_id(entity.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_repository_pagination(dummy_repo, db_session):
    # Bulk insert
    entities = [DummyEntity(name=f"item_{i}") for i in range(1, 16)]
    await dummy_repo.add_bulk(entities)
    await db_session.flush()
    
    # Paginate page 1
    req1 = PaginationRequest(page=1, page_size=10, sort=[SortOptions(field="id", direction=SortDirection.ASC)])
    resp1 = await dummy_repo.get_paginated(req1)
    
    assert resp1.total_count == 15
    assert len(resp1.items) == 10
    assert resp1.has_next is True
    assert resp1.items[0].name == "item_1"
    
    # Paginate page 2
    req2 = PaginationRequest(page=2, page_size=10, sort=[SortOptions(field="id", direction=SortDirection.ASC)])
    resp2 = await dummy_repo.get_paginated(req2)
    
    assert len(resp2.items) == 5
    assert resp2.has_next is False
    assert resp2.has_previous is True
