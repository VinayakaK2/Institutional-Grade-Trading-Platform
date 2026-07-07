import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.universe_engine.contracts.certification import IUniverseCertificationFacade
from backend.universe_engine.certification.pipeline import UniverseCertificationPipeline
from backend.universe_engine.certification.models import UniverseCertificationContext, UniverseCertificationConfiguration
from backend.universe_engine.certification.exceptions import CertificationVerificationError

class DummyFailStage:
    async def execute(self, context, facade):
        raise CertificationVerificationError("Dummy failure")

class DummyErrorStage:
    async def execute(self, context, facade):
        raise ValueError("Unexpected error")

@pytest.mark.asyncio
async def test_pipeline_halt_on_verification_error():
    pipeline = UniverseCertificationPipeline([DummyFailStage()])
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    from datetime import datetime, timezone
    context = UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))
    
    res = await pipeline.execute(context, mock_facade)
    assert res.is_certified is False
    assert "DummyFailStage_halted" in res.test_results

@pytest.mark.asyncio
async def test_pipeline_halt_on_unexpected_error():
    pipeline = UniverseCertificationPipeline([DummyErrorStage()])
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    from datetime import datetime, timezone
    context = UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))
    
    with pytest.raises(ValueError):
        await pipeline.execute(context, mock_facade)
    assert context.is_certified is False
    assert "DummyErrorStage_error" in context.test_results
