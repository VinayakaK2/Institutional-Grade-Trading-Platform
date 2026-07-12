import pytest
from backend.liquidity_grab_engine.certification.models.models import CertificationReport, CertificationSummary, CertificationPhaseResult, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.repository.memory import InMemoryCertificationRepository
from backend.liquidity_grab_engine.certification.repository.postgres import PostgreSQLCertificationRepository

def get_mock_report(report_id="1", ds_version="1", phases=[CertificationPhaseEnum.FOUNDATION]):
    pr = [CertificationPhaseResult(phase=p, success=True, execution_time_ms=10.0) for p in phases]
    summary = CertificationSummary(is_certified=True, total_execution_time_ms=10.0, phase_results=pr)
    return CertificationReport(
        report_id=report_id,
        dataset_metadata={"dataset_version": ds_version},
        environment_details={"env": "test"},
        summary=summary
    )

@pytest.mark.asyncio
async def test_memory_repository():
    repo = InMemoryCertificationRepository()
    
    rep1 = get_mock_report("1", "1", [CertificationPhaseEnum.FOUNDATION])
    rep2 = get_mock_report("2", "2", [CertificationPhaseEnum.DETECTION])
    
    assert await repo.exists("1") is False
    
    await repo.save(rep1)
    await repo.save(rep2)
    
    assert await repo.exists("1") is True
    
    # Immutability Check
    with pytest.raises(ValueError):
        await repo.save(rep1)
        
    loaded = await repo.load("1")
    assert loaded is not None
    assert loaded.report_id == "1"
    
    latest = await repo.load_latest()
    assert latest is not None
    assert latest.report_id == "2"
    
    # Queries
    by_phase = await repo.query_by_phase(CertificationPhaseEnum.DETECTION)
    assert len(by_phase) == 1
    assert by_phase[0].report_id == "2"
    
    by_version = await repo.query_by_version("1")
    assert len(by_version) == 1
    assert by_version[0].report_id == "1"

@pytest.mark.asyncio
async def test_postgres_repository_stub():
    repo = PostgreSQLCertificationRepository()
    rep = get_mock_report()
    
    with pytest.raises(NotImplementedError):
        await repo.save(rep)
        
    with pytest.raises(NotImplementedError):
        await repo.load("1")
        
    with pytest.raises(NotImplementedError):
        await repo.exists("1")
        
    with pytest.raises(NotImplementedError):
        await repo.load_latest()
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_phase(CertificationPhaseEnum.FOUNDATION)
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_version("1")
