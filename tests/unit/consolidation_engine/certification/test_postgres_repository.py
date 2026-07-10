import pytest
from backend.consolidation_engine.certification.repository.postgres import PostgreSQLConsolidationCertificationRepository
from backend.consolidation_engine.certification.models import ConsolidationCertificationReport
from datetime import datetime, timezone

@pytest.fixture
def repo():
    return PostgreSQLConsolidationCertificationRepository(session_factory=None)

@pytest.mark.asyncio
async def test_postgres_repo_stub(repo):
    ts = datetime.now(timezone.utc)
    report = ConsolidationCertificationReport(
        certification_id="cert1",
        pipeline_version="1.0",
        configuration_version=1,
        business_fingerprint_version="1.0",
        detection_algorithm_version="1.0",
        quality_algorithm_version="1.0",
        lifecycle_algorithm_version="1.0",
        optimization_algorithm_version="1.0",
        verification_results=[],
        generated_timestamp=ts
    )
    
    await repo.save(report)
    assert await repo.exists("cert1") is False
    assert await repo.load("cert1") is None
    assert await repo.load_latest() is None
    assert await repo.query_by_pipeline_version("1.0") == []
