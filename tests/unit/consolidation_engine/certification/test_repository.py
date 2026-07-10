import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.certification.repository.memory import InMemoryConsolidationCertificationRepository
from backend.consolidation_engine.certification.models import ConsolidationCertificationReport, CoverageSummary

@pytest.fixture
def repo():
    return InMemoryConsolidationCertificationRepository()
    
def create_report(cert_id: str, version: str) -> ConsolidationCertificationReport:
    ts = datetime.now(timezone.utc)
    return ConsolidationCertificationReport(
        certification_id=cert_id,
        pipeline_version=version,
        configuration_version=1,
        business_fingerprint_version="1.0",
        detection_algorithm_version="1.0",
        quality_algorithm_version="1.0",
        lifecycle_algorithm_version="1.0",
        optimization_algorithm_version="1.0",
        verification_results=[],
        generated_timestamp=ts
    )

@pytest.mark.asyncio
async def test_repo_save_and_load(repo):
    report = create_report("cert1", "1.0")
    await repo.save(report)
    
    assert await repo.exists("cert1") is True
    assert await repo.exists("cert2") is False
    
    loaded = await repo.load("cert1")
    assert loaded is not None
    assert loaded.certification_id == "cert1"

@pytest.mark.asyncio
async def test_repo_duplicate_save(repo):
    report = create_report("cert1", "1.0")
    await repo.save(report)
    
    with pytest.raises(ConsolidationRepositoryError):
        await repo.save(report)
        
@pytest.mark.asyncio
async def test_query_by_pipeline_version(repo):
    r1 = create_report("cert1", "1.0")
    r2 = create_report("cert2", "1.0")
    r3 = create_report("cert3", "2.0")
    
    await repo.save(r1)
    await repo.save(r2)
    await repo.save(r3)
    
    v1_reports = await repo.query_by_pipeline_version("1.0")
    assert len(v1_reports) == 2
    assert r1 in v1_reports
    assert r2 in v1_reports
    
    v2_reports = await repo.query_by_pipeline_version("2.0")
    assert len(v1_reports) == 2
