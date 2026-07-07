import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.universe_engine.contracts.certification import IUniverseCertificationFacade
from backend.universe_engine.certification.models import UniverseCertificationContext, UniverseCertificationConfiguration
from backend.universe_engine.certification.exceptions import CertificationVerificationError
from backend.universe_engine.certification.stages import (
    FunctionalCertificationStage,
    DeterminismCertificationStage,
    IntegrityCertificationStage,
    PerformanceCertificationStage,
    StressCertificationStage
)
from backend.universe_engine.classification.models import ClassifiedUniverse
from backend.universe_engine.optimization.models import OptimizedUniverse

@pytest.fixture
def context():
    config = UniverseCertificationConfiguration(mode="DETERMINISTIC")
    from datetime import datetime, timezone
    return UniverseCertificationContext(run_id="test1", config=config, started_at=datetime.now(timezone.utc))

@pytest.fixture
def facade():
    return AsyncMock(spec=IUniverseCertificationFacade)

@pytest.mark.asyncio
async def test_functional_failure_missing_snapshot(context, facade):
    facade.execute_full_pipeline.return_value = {}
    stage = FunctionalCertificationStage()
    
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.functional_passed is False

@pytest.mark.asyncio
async def test_determinism_failure_same_input(context, facade):
    mock_opt1 = MagicMock(spec=OptimizedUniverse)
    mock_opt1.symbol_fingerprints = {"AAPL": "hash1"}
    mock_opt2 = MagicMock(spec=OptimizedUniverse)
    mock_opt2.symbol_fingerprints = {"AAPL": "hash2"}
    
    facade.execute_full_pipeline.side_effect = [
        {"optimized_universe": mock_opt1},
        {"optimized_universe": mock_opt2},
        {"optimized_universe": mock_opt1}
    ]
    
    stage = DeterminismCertificationStage()
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.determinism_passed is False
    assert context.determinism_results["same_input_equivalence"] is False

@pytest.mark.asyncio
async def test_determinism_failure_incremental(context, facade):
    mock_opt1 = MagicMock(spec=OptimizedUniverse)
    mock_opt1.symbol_fingerprints = {"AAPL": "hash1"}
    mock_opt2 = MagicMock(spec=OptimizedUniverse)
    mock_opt2.symbol_fingerprints = {"AAPL": "hash2"}
    
    facade.execute_full_pipeline.side_effect = [
        {"optimized_universe": mock_opt1},
        {"optimized_universe": mock_opt1},
        {"optimized_universe": mock_opt2}
    ]
    
    stage = DeterminismCertificationStage()
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.determinism_passed is False
    assert context.determinism_results["incremental_equivalence"] is False

@pytest.mark.asyncio
async def test_determinism_failure_exception(context, facade):
    facade.execute_full_pipeline.side_effect = Exception("Internal Error")
    stage = DeterminismCertificationStage()
    
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.determinism_passed is False

@pytest.mark.asyncio
async def test_integrity_failure_lineage(context, facade):
    mock_opt = MagicMock()
    mock_opt.parent_classified_universe_id = "cls1"
    mock_cls = MagicMock()
    mock_cls.classified_universe_id = "cls2" # mismatch
    
    facade.execute_full_pipeline.return_value = {
        "optimized_universe": mock_opt,
        "classified_universe": mock_cls,
        "certified_universe": MagicMock(),
        "liquidity_universe": MagicMock(),
        "universe_snapshot": MagicMock()
    }
    
    stage = IntegrityCertificationStage()
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.integrity_passed is False

@pytest.mark.asyncio
async def test_stress_failure_repeated_runs(context, facade):
    mock_opt1 = MagicMock()
    mock_opt1.symbol_fingerprints = {"AAPL": "hash1"}
    mock_opt2 = MagicMock()
    mock_opt2.symbol_fingerprints = {"AAPL": "hash2"}
    
    # 3 scales + 1 baseline + N repeated
    def side_effect(*args, **kwargs):
        if "stress_rep_0" in args[0]:
            return {"optimized_universe": mock_opt2}
        return {"optimized_universe": mock_opt1}
        
    facade.execute_full_pipeline.side_effect = side_effect
    
    stage = StressCertificationStage()
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.stress_passed is False

@pytest.mark.asyncio
async def test_stress_failure_exception(context, facade):
    facade.execute_full_pipeline.side_effect = Exception("DB Timeout")
    stage = StressCertificationStage()
    with pytest.raises(CertificationVerificationError):
        await stage.execute(context, facade)
    assert context.stress_passed is False

@pytest.mark.asyncio
async def test_performance_execution(context, facade):
    stage = PerformanceCertificationStage()
    await stage.execute(context, facade)
    assert context.performance_metrics.execution_time_ms >= 0
    assert facade.execute_full_pipeline.call_count == 1
