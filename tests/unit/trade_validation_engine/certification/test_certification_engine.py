import pytest
import os
import shutil
from unittest.mock import AsyncMock
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import QualityGateStatus
from backend.trade_validation_engine.certification.di.container import CertificationContainer
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot, DecisionState
from backend.trade_validation_engine.optimization.repository.memory import InMemoryOptimizationRepository
from backend.trade_validation_engine.certification.engine.snapshot_hasher import SnapshotHasher
from datetime import datetime, timezone

@pytest.fixture
def mock_snapshot():
    return TradeDecisionSnapshot(
        decision_id="dec123",
        business_fingerprint="fp123",
        symbol="BTCUSD",
        timeframe="1H",
        dataset_version=1,
        decision_state=DecisionState.VALID,
        rejection_reasons=[],
        validation_report_version="1.0.0",
        stage_results=[],
        created_timestamp=datetime.now(timezone.utc),
        metadata={}
    )

@pytest.fixture
def mock_snapshot_mismatch():
    return TradeDecisionSnapshot(
        decision_id="dec123_bad",
        business_fingerprint="fp123",
        symbol="BTCUSD",
        timeframe="1H",
        dataset_version=1,
        decision_state=DecisionState.INVALID,
        rejection_reasons=[],
        validation_report_version="1.0.0",
        stage_results=[],
        created_timestamp=datetime.now(timezone.utc),
        metadata={"diff": True}
    )

@pytest.fixture
def test_config():
    return CertificationConfig(
        report_output_directory="test_evidence_dir",
        stress_batch_sizes=[10, 20],
        performance_iterations=2,
        allowed_memory_growth_mb=1000.0,  # make sure it passes memory stress
    )

@pytest.fixture(autouse=True)
def cleanup(test_config):
    yield
    if os.path.exists(test_config.report_output_directory):
        shutil.rmtree(test_config.report_output_directory)

@pytest.mark.asyncio
async def test_full_certification_pipeline_success(test_config, mock_snapshot):
    mock_engine = AsyncMock()
    mock_engine.execute_batch.return_value = [(i, mock_snapshot) for i in range(10)]
    
    mock_repo = InMemoryOptimizationRepository()
    
    container = CertificationContainer(test_config)
    engine = container.engine()
    
    original_execute = engine.run_certification
    
    async def patched_run(gates):
        for stage in engine._stages:
            orig_stage_execute = stage.execute
            async def wrapped_execute(config, ctx, s=stage, orig=orig_stage_execute):
                ctx["optimization_engine"] = mock_engine
                ctx["optimization_repository"] = mock_repo
                ctx["functional_dataset"] = ["mock_input_1", "mock_input_2"]
                ctx["golden_dataset"] = ["mock_input_1", "mock_input_2"]
                # Match expected vs actual for Regression Verification
                ctx["expected_snapshots"] = [mock_snapshot.model_dump() for _ in range(2)]
                mock_engine.execute_batch.return_value = [(i, mock_snapshot) for i in range(2)]
                return await orig(config, ctx)
            stage.execute = wrapped_execute
            
        return await original_execute(gates)
    
    gates = QualityGateStatus(
        ruff_status="PASS",
        mypy_status="PASS",
        bandit_status="PASS",
        pytest_status="PASS",
        coverage_percentage=95.0
    )
    
    report = await patched_run(gates)
    
    assert report.overall_result == "CERTIFIED"
    assert len(report.stage_results) == 6
    for stage in report.stage_results:
        assert stage.status == "PASS"

@pytest.mark.asyncio
async def test_certification_skip_and_fail_fast():
    config = CertificationConfig(
        report_output_directory="test_evidence_dir_2",
        enable_functional_verification=False, # should skip
        fail_fast=True
    )
    container = CertificationContainer(config)
    engine = container.engine()
    
    # We will force the determinism stage to throw an exception to test fail_fast
    async def bad_execute(cfg, ctx):
        raise ValueError("Simulated stage crash")
        
    engine._stages[1].execute = bad_execute
    
    gates = QualityGateStatus(
        ruff_status="PASS",
        mypy_status="PASS",
        bandit_status="PASS",
        pytest_status="PASS",
        coverage_percentage=95.0
    )
    
    report = await engine.run_certification(gates)
    assert report.overall_result == "FAILED"
    assert report.stage_results[0].status == "SKIP"
    assert report.stage_results[1].status == "FAIL"
    # Due to fail fast, we shouldn't have 6 results
    assert len(report.stage_results) == 2
    
    if os.path.exists(config.report_output_directory):
        shutil.rmtree(config.report_output_directory)

@pytest.mark.asyncio
async def test_repository_mutation_rejection(test_config):
    from backend.trade_validation_engine.certification.stages.repository_verification_stage import RepositoryVerificationStage
    
    stage = RepositoryVerificationStage()
    
    class BadRepo:
        def update(self): pass
        
    ctx = {"optimization_repository": BadRepo()}
    res = await stage.execute(test_config, ctx)
    assert res.status == "FAIL"

@pytest.mark.asyncio
async def test_regression_mismatch(test_config, mock_snapshot, mock_snapshot_mismatch):
    from backend.trade_validation_engine.certification.stages.regression_verification_stage import RegressionVerificationStage
    stage = RegressionVerificationStage()
    
    mock_engine = AsyncMock()
    mock_engine.execute_batch.return_value = [(0, mock_snapshot_mismatch)]
    
    ctx = {
        "golden_dataset": ["input1"],
        "expected_snapshots": [mock_snapshot.model_dump()],
        "optimization_engine": mock_engine
    }
    
    res = await stage.execute(test_config, ctx)
    assert res.status == "FAIL"

@pytest.mark.asyncio
async def test_stress_memory_leak(test_config, mock_snapshot):
    from backend.trade_validation_engine.certification.stages.stress_verification_stage import StressVerificationStage
    stage = StressVerificationStage()
    
    mock_engine = AsyncMock()
    mock_engine.execute_batch.return_value = [(0, mock_snapshot)]
    
    config = CertificationConfig(
        stress_batch_sizes=[1],
        allowed_memory_growth_mb=-1.0 # Force a failure since memory will always grow > -1
    )
    
    ctx = {
        "functional_dataset": ["input1"],
        "optimization_engine": mock_engine
    }
    
    res = await stage.execute(config, ctx)
    assert res.status == "FAIL"
    assert "Memory leak detected" in str(res.metrics)
    
def test_snapshot_hasher():
    data = {"b": 1, "a": 2, "c": [3, 2, 1], "d": {"z": 1, "y": 2}}
    h1 = SnapshotHasher.generate_fingerprint(data)
    
    # Out of order dict should hash to the same because of sort_keys=True
    data2 = {"a": 2, "c": [3, 2, 1], "d": {"y": 2, "z": 1}, "b": 1}
    h2 = SnapshotHasher.generate_fingerprint(data2)
    
    assert h1 == h2
