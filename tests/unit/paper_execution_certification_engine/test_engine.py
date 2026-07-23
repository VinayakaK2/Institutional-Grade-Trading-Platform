import pytest
from unittest.mock import patch, MagicMock
from backend.paper_execution_certification_engine.engine.engine import PaperExecutionCertificationEngine
from backend.paper_execution_certification_engine.repository.memory_repo import MemoryPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.config.config import CertificationConfig
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext
from backend.paper_execution_optimization_engine.config.config import OptimizationConfig
from backend.paper_execution_certification_engine.exceptions.exceptions import CertificationFailedError
from backend.paper_execution_certification_engine.engine.pipeline import PaperExecutionCertificationPipeline

class MockSnapshot:
    def __init__(self, fp):
        self.business_fingerprint = fp
        self.snapshot_version = f"snap_{fp}"

@pytest.fixture
def mock_context():
    exec_ctx = PaperExecutionResultExecutionContext.model_construct(
        dataset_version="ds_1",
        configuration_hash="hash_1",
        portfolio_decision_snapshot=MockSnapshot("pds"),
        paper_order_snapshot=MockSnapshot("order_1"),
        paper_fill_snapshot=MockSnapshot("fill_1"),
        paper_execution_quality_snapshot=MockSnapshot("peqs")
    )
    opt_ctx = PaperExecutionOptimizationContext(
        execution_context=exec_ctx,
        optimization_configuration=OptimizationConfig(caching_enabled=True, configuration_hash="opt_1"),
        optimization_metadata={}
    )
    return PaperExecutionCertificationContext(
        optimization_context=opt_ctx,
        synthetic_dataset_a_id="ds_a",
        synthetic_dataset_a_hash="hash_a",
        synthetic_dataset_b_id="ds_b",
        synthetic_dataset_b_hash="hash_b",
        replay_dataset_id="ds_replay",
        replay_dataset_hash="hash_replay",
        stress_dataset_id="ds_stress",
        stress_dataset_hash="hash_stress",
        certification_configuration=CertificationConfig(stress_execution_counts=[10, 50, 100])
    )

class MockOptSnapshot:
    def __init__(self, ch):
        self.canonical_hash = ch

@pytest.fixture(autouse=True)
def mock_optimization_engine_batch():
    def mock_batch(*args, **kwargs):
        contexts = kwargs.get("contexts") or args[0]
        return [(MockOptSnapshot("ch"), MockSnapshot("bfp")) for _ in contexts]
        
    with patch("backend.paper_execution_optimization_engine.engine.engine.PaperExecutionOptimizationEngine.execute_batch") as mock_exec:
        mock_exec.side_effect = mock_batch
        yield mock_exec

@pytest.mark.asyncio
async def test_engine_success(mock_context):
    repo = MemoryPaperExecutionCertificationRepository()
    engine = PaperExecutionCertificationEngine(repo)
    
    snapshot = await engine.certify(mock_context)
    
    assert snapshot is not None
    assert snapshot.certification_report.certified is True
    assert len(snapshot.certification_report.verified_stages) == 8
    
    # Check that it's in the repo
    assert await repo.exists(snapshot.snapshot_version)

@pytest.mark.asyncio
async def test_engine_failure_fail_fast(mock_context):
    repo = MemoryPaperExecutionCertificationRepository()
    engine = PaperExecutionCertificationEngine(repo)
    
    # Mock one of the stages to fail
    with patch("backend.paper_execution_certification_engine.engine.stages.functional.FunctionalVerificationStage._run_verification") as mock_stage:
        mock_stage.side_effect = Exception("Synthetic failure")
        
        with pytest.raises(CertificationFailedError):
            await engine.certify(mock_context)
            
@pytest.mark.asyncio
async def test_engine_failure_no_fail_fast(mock_context):
    # Context with fail_fast=False
    ctx = PaperExecutionCertificationContext.model_copy(
        mock_context, 
        update={"certification_configuration": CertificationConfig(fail_fast=False)}
    )
    
    repo = MemoryPaperExecutionCertificationRepository()
    engine = PaperExecutionCertificationEngine(repo)
    
    # Mock one of the stages to fail
    with patch("backend.paper_execution_certification_engine.engine.stages.functional.FunctionalVerificationStage._run_verification") as mock_stage:
        mock_stage.side_effect = Exception("Synthetic failure")
        
        # It shouldn't raise immediately inside pipeline, but the engine should raise 
        # CertificationFailedError when checking the results at the end.
        with pytest.raises(CertificationFailedError, match="Certification failed at stage: Functional Verification"):
            await engine.certify(ctx)
