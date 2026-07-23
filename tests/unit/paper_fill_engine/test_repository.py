import pytest
from backend.paper_fill_engine.repository.memory_repo import MemoryPaperFillRepository
from backend.paper_fill_engine.repository.postgres_repo import PostgreSQLPaperFillRepository
from backend.paper_fill_engine.builders.snapshot_builder import PaperFillSnapshotBuilder
from backend.paper_fill_engine.exceptions.exceptions import PaperFillPersistenceError
from backend.paper_fill_engine.core.stages import DeterministicFillStage
from backend.paper_fill_engine.models.contexts import PaperFillPipelineContext

async def build_snapshot(dummy_context):
    pipeline_context = PaperFillPipelineContext(execution_context=dummy_context)
    stage = DeterministicFillStage()
    await stage.execute(dummy_context, pipeline_context)
    
    builder = PaperFillSnapshotBuilder()
    return builder.build(dummy_context, pipeline_context)

@pytest.mark.asyncio
async def test_memory_repo_save_load(dummy_context):
    snapshot = await build_snapshot(dummy_context)
    repo = MemoryPaperFillRepository()
    assert not repo.exists(snapshot.snapshot_id)
    repo.save(snapshot)
    assert repo.exists(snapshot.snapshot_id)
    
    loaded = repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_memory_repo_duplicate_save(dummy_context):
    snapshot = await build_snapshot(dummy_context)
    repo = MemoryPaperFillRepository()
    repo.save(snapshot)
    
    with pytest.raises(PaperFillPersistenceError):
        repo.save(snapshot)

@pytest.mark.asyncio
async def test_postgres_repo_not_implemented(dummy_context):
    snapshot = await build_snapshot(dummy_context)
    repo = PostgreSQLPaperFillRepository()
    with pytest.raises(NotImplementedError):
        repo.save(snapshot)
    with pytest.raises(NotImplementedError):
        repo.load(snapshot.snapshot_id)
    with pytest.raises(NotImplementedError):
        repo.exists(snapshot.snapshot_id)
    with pytest.raises(NotImplementedError):
        repo.load_latest()
