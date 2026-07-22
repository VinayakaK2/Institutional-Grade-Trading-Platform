import pytest
from backend.paper_order_engine.repository.memory_repo import MemoryPaperOrderRepository
from backend.paper_order_engine.repository.postgres_repo import PostgreSQLPaperOrderRepository
from backend.paper_order_engine.builders.snapshot_builder import PaperOrderSnapshotBuilder
from backend.paper_order_engine.exceptions.exceptions import PaperOrderPersistenceError

@pytest.fixture
def snapshot(dummy_context, dummy_pipeline_context):
    builder = PaperOrderSnapshotBuilder()
    return builder.build(dummy_context, dummy_pipeline_context)

def test_memory_repo_save_load(snapshot):
    repo = MemoryPaperOrderRepository()
    assert not repo.exists(snapshot.snapshot_id)
    repo.save(snapshot)
    assert repo.exists(snapshot.snapshot_id)
    
    loaded = repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

def test_memory_repo_duplicate_save(snapshot):
    repo = MemoryPaperOrderRepository()
    repo.save(snapshot)
    
    with pytest.raises(PaperOrderPersistenceError):
        repo.save(snapshot)

def test_memory_repo_load_latest(snapshot):
    repo = MemoryPaperOrderRepository()
    repo.save(snapshot)
    
    latest = repo.load_latest()
    assert latest == snapshot

def test_memory_repo_load_by_version(snapshot):
    repo = MemoryPaperOrderRepository()
    repo.save(snapshot)
    
    loaded = repo.load_by_snapshot_version(snapshot.snapshot_version)
    assert loaded == snapshot

def test_postgres_repo_not_implemented(snapshot):
    repo = PostgreSQLPaperOrderRepository()
    with pytest.raises(NotImplementedError):
        repo.save(snapshot)
    with pytest.raises(NotImplementedError):
        repo.load(snapshot.snapshot_id)
    with pytest.raises(NotImplementedError):
        repo.exists(snapshot.snapshot_id)
    with pytest.raises(NotImplementedError):
        repo.load_latest()
    with pytest.raises(NotImplementedError):
        repo.load_by_snapshot_version("some-version")
