import pytest
from backend.paper_execution_result_engine.repository.memory_repo import MemoryPaperExecutionResultRepository
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultPersistenceError
from backend.paper_execution_result_engine.services.query_service import PaperExecutionResultQueryService

def test_memory_repo_save_load(mock_execution_context):
    from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
    snapshot = PaperExecutionResultEngine().execute(mock_execution_context)
    
    repo = MemoryPaperExecutionResultRepository()
    repo.save(snapshot)
    
    loaded = repo.load(snapshot.snapshot_version)
    assert loaded == snapshot
    
    latest = repo.load_latest()
    assert latest == snapshot
    
    all_snaps = repo.list_all()
    assert len(all_snaps) == 1
    
def test_memory_repo_append_only(mock_execution_context):
    from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
    snapshot = PaperExecutionResultEngine().execute(mock_execution_context)
    
    repo = MemoryPaperExecutionResultRepository()
    repo.save(snapshot)
    
    with pytest.raises(PaperExecutionResultPersistenceError, match="already exists"):
        repo.save(snapshot)

def test_memory_repo_not_found():
    repo = MemoryPaperExecutionResultRepository()
    with pytest.raises(PaperExecutionResultPersistenceError, match="not found"):
        repo.load("missing")
    assert repo.load_latest() is None
        
def test_query_service(mock_execution_context):
    from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
    snapshot = PaperExecutionResultEngine().execute(mock_execution_context)
    
    repo = MemoryPaperExecutionResultRepository()
    repo.save(snapshot)
    
    service = PaperExecutionResultQueryService(repo)
    
    assert len(service.query_by_status(snapshot.execution_status)) == 1
    assert len(service.query_by_parent_order_snapshot("ord_1")) == 1
    assert len(service.query_by_parent_fill_snapshot("fill_snap_1")) == 1
    assert len(service.query_by_symbol("AAPL")) == 1
    assert len(service.query_by_timeframe("2000-01-01", "2099-01-01")) == 1
    assert service.query_by_snapshot_version(snapshot.snapshot_version) == snapshot
    assert service.query_by_snapshot_version("missing") is None
