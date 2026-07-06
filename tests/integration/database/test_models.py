"""
Integration tests for ORM models and mixins.
"""
import pytest
from sqlalchemy import select
from tests.integration.database.conftest import DummyAuditableModel, DummySoftDeleteModel

@pytest.mark.asyncio
async def test_uuid_generation(db_session):
    """Verifies that the UUID string is generated automatically on insertion."""
    obj = DummyAuditableModel(dummy_name="test1")
    db_session.add(obj)
    await db_session.commit()
    
    assert obj.id is not None
    assert isinstance(obj.id, str)
    assert len(obj.id) == 36 # UUID4 string length

@pytest.mark.asyncio
async def test_auditable_model_timestamps(db_session):
    """Verifies created_at and updated_at behave correctly."""
    obj = DummyAuditableModel(dummy_name="test2", created_by="user1")
    db_session.add(obj)
    await db_session.commit()
    
    assert obj.created_at is not None
    assert obj.updated_at is not None
    assert obj.created_at == obj.updated_at
    assert obj.version == 1

@pytest.mark.asyncio
async def test_soft_delete_model(db_session):
    """Verifies that soft_delete marks the record but does not drop it."""
    obj = DummySoftDeleteModel(dummy_name="test_soft")
    db_session.add(obj)
    await db_session.commit()
    
    assert obj.is_deleted is False
    assert obj.deleted_at is None
    
    obj.soft_delete()
    await db_session.commit()
    
    assert obj.is_deleted is True
    assert obj.deleted_at is not None
    
    # Verify it still exists in the DB
    result = await db_session.execute(
        select(DummySoftDeleteModel).where(DummySoftDeleteModel.id == obj.id)
    )
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.is_deleted is True
