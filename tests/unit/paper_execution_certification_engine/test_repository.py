import pytest
from datetime import datetime, timezone
from backend.paper_execution_certification_engine.repository.memory_repo import MemoryPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.repository.postgres_repo import PostgresPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.query.service import PaperExecutionCertificationQueryService
from backend.paper_execution_certification_engine.models.snapshot import (
    PaperExecutionCertificationSnapshot,
    CertificationReport,
    CertificationMetadata
)
from backend.paper_execution_certification_engine.exceptions.exceptions import (
    CertificationRepositoryIntegrityError,
    CertificationRepositoryNotFoundError
)

@pytest.fixture
def dummy_snapshot():
    report = CertificationReport(
        certification_id="cert-1",
        certification_schema_version="1.0.0",
        certified=True,
        paper_execution_version="1.0",
        optimization_version="1.0",
        certification_version="1.0",
        timestamp="time",
        business_fingerprint="bfp",
        canonical_hash="ch",
        evidence_count=0,
        verified_stages=[]
    )
    return PaperExecutionCertificationSnapshot(
        snapshot_version="v1",
        certification_id="cert-1",
        certification_version="1.0",
        certification_report=report,
        business_fingerprint="bfp",
        canonical_hash="ch",
        parent_execution_snapshot_version="parent_1",
        certification_metadata=CertificationMetadata(certified_at=datetime.now(timezone.utc), execution_duration_ms=10.0)
    )

@pytest.mark.asyncio
async def test_memory_repo_append_only(dummy_snapshot):
    repo = MemoryPaperExecutionCertificationRepository()
    
    # Save works
    await repo.save(dummy_snapshot)
    assert await repo.exists("v1")
    
    # Duplicate save raises error
    with pytest.raises(CertificationRepositoryIntegrityError):
        await repo.save(dummy_snapshot)
        
    loaded = await repo.load("v1")
    assert loaded == dummy_snapshot
    
@pytest.mark.asyncio
async def test_memory_repo_not_found():
    repo = MemoryPaperExecutionCertificationRepository()
    with pytest.raises(CertificationRepositoryNotFoundError):
        await repo.load("missing")

@pytest.mark.asyncio
async def test_query_service(dummy_snapshot):
    repo = MemoryPaperExecutionCertificationRepository()
    await repo.save(dummy_snapshot)
    
    qs = PaperExecutionCertificationQueryService(repo)
    
    latest = await qs.query_by_execution_snapshot("parent_1")
    assert latest is not None
    assert latest.snapshot_version == "v1"
    
    empty = await qs.query_by_execution_snapshot("parent_unknown")
    assert empty is None
    
    by_version = await qs.query_by_certification_version("v1")
    assert by_version == dummy_snapshot

@pytest.mark.asyncio
async def test_postgres_repo_stub():
    repo = PostgresPaperExecutionCertificationRepository()
    with pytest.raises(NotImplementedError):
        await repo.save(None)
    with pytest.raises(NotImplementedError):
        await repo.load("v")
    with pytest.raises(NotImplementedError):
        await repo.exists("v")
    with pytest.raises(NotImplementedError):
        await repo.load_latest("p")
