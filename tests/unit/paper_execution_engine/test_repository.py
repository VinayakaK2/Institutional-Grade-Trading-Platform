import pytest
from backend.paper_execution_engine.repository.memory_repo import MemoryPaperExecutionRepository
from backend.paper_execution_engine.repository.postgres_repo import PostgreSQLPaperExecutionRepository
from backend.paper_execution_engine.builders.snapshot_builder import PaperExecutionSnapshotBuilder

@pytest.fixture
def snapshot(dummy_context, dummy_pipeline_context):
    builder = PaperExecutionSnapshotBuilder()
    return builder.build(dummy_context, dummy_pipeline_context)

@pytest.mark.asyncio
async def test_memory_repo_save_load(snapshot):
    repo = MemoryPaperExecutionRepository()
    
    assert not await repo.exists(snapshot.snapshot_id)
    
    await repo.save(snapshot)
    
    assert await repo.exists(snapshot.snapshot_id)
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_memory_repo_load_latest(snapshot):
    repo = MemoryPaperExecutionRepository()
    await repo.save(snapshot)
    
    latest = await repo.load_latest()
    assert latest == snapshot

@pytest.mark.asyncio
async def test_memory_repo_load_by_version(snapshot):
    repo = MemoryPaperExecutionRepository()
    await repo.save(snapshot)
    
    loaded = await repo.load_by_snapshot_version(snapshot.snapshot_version)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_memory_repo_duplicate_save(snapshot):
    repo = MemoryPaperExecutionRepository()
    await repo.save(snapshot)
    
    with pytest.raises(ValueError, match="Duplicate snapshot ID"):
        await repo.save(snapshot)

@pytest.mark.asyncio
async def test_postgres_repo_not_implemented(snapshot):
    repo = PostgreSQLPaperExecutionRepository()
    with pytest.raises(NotImplementedError):
        await repo.save(snapshot)
