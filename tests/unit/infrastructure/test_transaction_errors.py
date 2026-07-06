import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from backend.infrastructure.database.utils.transaction import transactional
from backend.infrastructure.database.exceptions import DatabaseIntegrityException, DatabaseTransactionException

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_transactional_success(mock_session):
    @transactional
    async def dummy_func(session=None):
        return True
        
    result = await dummy_func(session=mock_session)
    assert result is True
    # since owns_session is False, commit should not be called
    mock_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_transactional_integrity_error(mock_session):
    @transactional
    async def dummy_func(session=None):
        orig_err = Exception("orig")
        raise IntegrityError("stmt", "params", orig_err)
        
    with pytest.raises(DatabaseIntegrityException):
        await dummy_func(session=mock_session)
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_transactional_sqlalchemy_error(mock_session):
    @transactional
    async def dummy_func(session=None):
        raise SQLAlchemyError("db error")
        
    with pytest.raises(DatabaseTransactionException):
        await dummy_func(session=mock_session)

@pytest.mark.asyncio
async def test_transactional_general_error(mock_session):
    @transactional
    async def dummy_func(session=None):
        raise ValueError("General Error")
        
    with pytest.raises(ValueError):
        await dummy_func(session=mock_session)
