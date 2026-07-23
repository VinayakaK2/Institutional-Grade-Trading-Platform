import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from backend.paper_execution_optimization_engine.repository.postgres_repo import PostgreSQLPaperExecutionOptimizationRepository, OptimizationRepositoryIntegrityError
from backend.paper_execution_optimization_engine.repository.memory_repo import MemoryPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot, OptimizationRuntimeStatistics

@pytest.fixture
def sample_snapshot():
    return PaperExecutionOptimizationSnapshot(
        optimization_fingerprint="fp1",
        business_fingerprint="biz1",
        canonical_hash="hash1",
        snapshot_version="snap1",
        optimization_summary=OptimizationRuntimeStatistics(),
        metadata={}
    )
@pytest.fixture
def sqlite_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE paper_execution_optimization_snapshots (
                optimization_fingerprint TEXT PRIMARY KEY,
                snapshot_version TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
    return engine

@pytest.mark.asyncio
async def test_memory_repo_save_and_load(sample_snapshot):
    repo = MemoryPaperExecutionOptimizationRepository()
    await repo.save(sample_snapshot)
    
    loaded = await repo.load("fp1")
    assert loaded == sample_snapshot
    
    latest = await repo.load_latest()
    assert latest == sample_snapshot

@pytest.mark.asyncio
async def test_memory_repo_duplicate_insert(sample_snapshot):
    repo = MemoryPaperExecutionOptimizationRepository()
    await repo.save(sample_snapshot)
    
    with pytest.raises(OptimizationRepositoryIntegrityError):
        await repo.save(sample_snapshot)

@pytest.mark.asyncio
async def test_postgres_repo_save_and_load(sqlite_engine, sample_snapshot):
    repo = PostgreSQLPaperExecutionOptimizationRepository(sqlite_engine)
    await repo.save(sample_snapshot)
    
    loaded = await repo.load("fp1")
    assert loaded == sample_snapshot
    
    latest = await repo.load_latest()
    assert latest == sample_snapshot

@pytest.mark.asyncio
async def test_postgres_repo_duplicate_insert(sqlite_engine, sample_snapshot):
    repo = PostgreSQLPaperExecutionOptimizationRepository(sqlite_engine)
    await repo.save(sample_snapshot)
    
    with pytest.raises(OptimizationRepositoryIntegrityError):
        await repo.save(sample_snapshot)
