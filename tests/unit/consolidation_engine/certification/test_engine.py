import pytest
import asyncio
from unittest.mock import MagicMock
from backend.consolidation_engine.certification.engine import ConsolidationCertificationEngine
from backend.consolidation_engine.certification.repository.memory import InMemoryConsolidationCertificationRepository
from backend.consolidation_engine.certification.models import VerificationStageStatus
from backend.consolidation_engine.pipeline.pipeline import ConsolidationPipeline

@pytest.fixture
def repo():
    return InMemoryConsolidationCertificationRepository()

@pytest.fixture
def pipeline():
    # We mock the pipeline specifically to ensure certification tests don't crash without all modules built yet.
    mock_pipeline = MagicMock(spec=ConsolidationPipeline)
    mock_pipeline.execute.return_value = None
    return mock_pipeline

@pytest.mark.asyncio
async def test_full_certification_execution(repo, pipeline):
    engine = ConsolidationCertificationEngine(repository=repo, pipeline=pipeline)
    
    report = await engine.execute_full_certification()
    
    assert report is not None
    assert len(report.verification_results) == 7
    assert all(r.status == VerificationStageStatus.PASSED for r in report.verification_results)
    
    # Assert saving to repo worked
    assert await repo.exists(report.certification_id) is True
    
    loaded = await repo.load_latest()
    assert loaded.certification_id == report.certification_id
    
@pytest.mark.asyncio
async def test_functional_failure(repo, pipeline):
    pipeline.execute.side_effect = Exception("Synthetic failure")
    
    engine = ConsolidationCertificationEngine(repository=repo, pipeline=pipeline)
    report = await engine.execute_full_certification()
    
    functional_result = next(r for r in report.verification_results if r.stage_name == "Functional Verification")
    assert functional_result.status == VerificationStageStatus.FAILED
    assert functional_result.error_message == "Synthetic failure"

@pytest.mark.asyncio
async def test_missing_latest_report(repo, pipeline):
    engine = ConsolidationCertificationEngine(repository=repo, pipeline=pipeline)
    loaded = await repo.load_latest()
    assert loaded is None
