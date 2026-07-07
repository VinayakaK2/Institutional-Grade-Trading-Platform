import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.universe_engine.contracts.certification import IUniverseCertificationFacade, IUniverseCertificationRepository
from backend.universe_engine.certification.pipeline import UniverseCertificationPipeline
from backend.universe_engine.certification.models import UniverseCertificationConfiguration, UniverseCertificationContext
from backend.universe_engine.certification.engine import UniverseCertificationEngine

@pytest.mark.asyncio
async def test_engine_generate_certification():
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    
    mock_pipeline = AsyncMock(spec=UniverseCertificationPipeline)
    from datetime import datetime, timezone
    mock_context = UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))
    mock_context.is_certified = True
    mock_pipeline.execute.return_value = mock_context
    
    mock_repo = AsyncMock(spec=IUniverseCertificationRepository)
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    
    engine = UniverseCertificationEngine(
        config=config,
        pipeline=mock_pipeline,
        repository=mock_repo,
        facade=mock_facade
    )
    
    res = await engine.generate_certification(run_id="test1")
    
    assert res.report is not None
    assert res.report.is_certified is True
    assert mock_repo.save_certification_report.call_count == 1

@pytest.mark.asyncio
async def test_engine_save_failure():
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    
    mock_pipeline = AsyncMock(spec=UniverseCertificationPipeline)
    from datetime import datetime, timezone
    mock_context = UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))
    mock_pipeline.execute.return_value = mock_context
    
    mock_repo = AsyncMock(spec=IUniverseCertificationRepository)
    mock_repo.save_certification_report.side_effect = Exception("DB Error")
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    
    engine = UniverseCertificationEngine(
        config=config,
        pipeline=mock_pipeline,
        repository=mock_repo,
        facade=mock_facade
    )
    
    with pytest.raises(Exception):
        await engine.generate_certification(run_id="test1")

@pytest.mark.asyncio
async def test_engine_read_only_regression():
    """
    Regression Test: Ensures that the Certification Engine acts purely as a read-only 
    verification layer and never attempts to mutate business domains.
    It verifies that the Engine ONLY calls `save_certification_report` on its own repository
    and NEVER calls any other persistence layer or attempts to modify universe snapshots.
    """
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    
    mock_pipeline = AsyncMock(spec=UniverseCertificationPipeline)
    from datetime import datetime, timezone
    mock_context = UniverseCertificationContext(run_id="test_ro", config=config, started_at=datetime.now(timezone.utc))
    mock_pipeline.execute.return_value = mock_context
    
    mock_repo = AsyncMock(spec=IUniverseCertificationRepository)
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    
    engine = UniverseCertificationEngine(
        config=config,
        pipeline=mock_pipeline,
        repository=mock_repo,
        facade=mock_facade
    )
    
    await engine.generate_certification(run_id="test_ro")
    
    # The only persistent interaction the Certification Engine should ever do 
    # is saving its own report to the certification repository.
    assert mock_repo.save_certification_report.call_count == 1
    # Verify no other repository methods (like load) or unexpected side effects occurred
    assert mock_repo.load_certification_report.call_count == 0
    
    # The engine orchestrates pipeline execution, which shouldn't directly use the facade 
    # (the stages use the facade).
    assert mock_facade.execute_full_pipeline.call_count == 0
