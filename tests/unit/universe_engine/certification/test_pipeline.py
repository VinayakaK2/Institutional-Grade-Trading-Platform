import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.universe_engine.contracts.certification import IUniverseCertificationFacade
from backend.universe_engine.certification.pipeline import UniverseCertificationPipeline
from backend.universe_engine.certification.models import UniverseCertificationContext, UniverseCertificationConfiguration
from backend.universe_engine.certification.stages import (
    FunctionalCertificationStage,
    DeterminismCertificationStage,
    IntegrityCertificationStage
)
from backend.universe_engine.classification.models import ClassifiedUniverse, ClassifiedSymbol
from backend.universe_engine.optimization.models import OptimizedUniverse

@pytest.mark.asyncio
async def test_pipeline_execution():
    stages = [
        FunctionalCertificationStage(),
        DeterminismCertificationStage(),
        IntegrityCertificationStage()
    ]
    pipeline = UniverseCertificationPipeline(stages)
    
    mock_facade = AsyncMock(spec=IUniverseCertificationFacade)
    
    # Mocking what the facade returns
    # Functional needs a specific dict return
    
    mock_opt_u = MagicMock(spec=OptimizedUniverse)
    mock_opt_u.symbol_fingerprints = {"AAPL": "hash1"}
    mock_opt_u.parent_classified_universe_id = "cls1"
    
    mock_cls_u = MagicMock(spec=ClassifiedUniverse)
    mock_cls_u.classified_universe_id = "cls1"
    mock_cls_u.parent_certified_universe_id = "crt1"
    
    mock_crt_u = MagicMock()
    mock_crt_u.certified_universe_id = "crt1"
    mock_crt_u.parent_liquidity_universe_id = "liq1"
    
    mock_liq_u = MagicMock()
    mock_liq_u.liquidity_universe_id = "liq1"
    mock_liq_u.parent_snapshot_id = "snap1"
    
    mock_snap = MagicMock()
    mock_snap.snapshot_id = "snap1"
    
    mock_facade.execute_full_pipeline.return_value = {
        "universe_snapshot": mock_snap,
        "liquidity_universe": mock_liq_u,
        "certified_universe": mock_crt_u,
        "classified_universe": mock_cls_u,
        "optimized_universe": mock_opt_u
    }
    
    from datetime import datetime, timezone
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    context = UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))
    
    res = await pipeline.execute(context, mock_facade)
    
    # Since stress stage is not included, stress_passed is True by default
    assert res.functional_passed is True
    assert res.determinism_passed is True
    assert res.integrity_passed is True
    assert res.is_certified is True
    
    assert mock_facade.execute_full_pipeline.call_count == 5 # 1 func, 3 det, 1 integ
    assert mock_facade.execute_full_pipeline.call_count == 5
