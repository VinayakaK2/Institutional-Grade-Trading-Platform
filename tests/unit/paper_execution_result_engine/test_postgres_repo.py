import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.paper_execution_result_engine.repository.postgres_repo import PostgreSQLPaperExecutionResultRepository
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultPersistenceError

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_snapshot(mock_execution_context):
    from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
    return PaperExecutionResultEngine().execute(mock_execution_context)

def test_postgres_repo_save_success(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchone.return_value = None # exists = False
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    repo.save(mock_snapshot)
    mock_session.commit.assert_called_once()
    
def test_postgres_repo_save_duplicate(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchone.return_value = (1,) # exists = True
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    with pytest.raises(PaperExecutionResultPersistenceError, match="already exists"):
        repo.save(mock_snapshot)
    mock_session.rollback.assert_called_once()
    
def test_postgres_repo_save_db_error(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchone.return_value = None # exists = False
    mock_session.commit.side_effect = Exception("DB connection failed")
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    with pytest.raises(PaperExecutionResultPersistenceError, match="Failed to save snapshot"):
        repo.save(mock_snapshot)
    mock_session.rollback.assert_called_once()
    
def test_postgres_repo_load_success(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchone.return_value = (mock_snapshot.model_dump_json(),)
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    loaded = repo.load(mock_snapshot.snapshot_version)
    assert loaded == mock_snapshot

def test_postgres_repo_load_missing(mock_session):
    mock_session.execute.return_value.fetchone.return_value = None
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    with pytest.raises(PaperExecutionResultPersistenceError, match="not found"):
        repo.load("missing_ver")

def test_postgres_repo_load_latest(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchone.return_value = (mock_snapshot.model_dump_json(),)
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    loaded = repo.load_latest()
    assert loaded == mock_snapshot

def test_postgres_repo_load_latest_empty(mock_session):
    mock_session.execute.return_value.fetchone.return_value = None
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    assert repo.load_latest() is None

def test_postgres_repo_list_all(mock_session, mock_snapshot):
    mock_session.execute.return_value.fetchall.return_value = [(mock_snapshot.model_dump_json(),)]
    repo = PostgreSQLPaperExecutionResultRepository(mock_session)
    results = repo.list_all()
    assert len(results) == 1
    assert results[0] == mock_snapshot
