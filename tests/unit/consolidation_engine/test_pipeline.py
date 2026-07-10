import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.pipeline.pipeline import ConsolidationPipeline
from backend.consolidation_engine.pipeline.stages.base import IConsolidationStage
from backend.consolidation_engine.models.models import ConsolidationSnapshot, ConsolidationExecutionContext, ConsolidationMetadata
from backend.consolidation_engine.config.config import ConsolidationConfiguration

class DummyStagePass(IConsolidationStage):
    def execute(self, context, snapshot):
        return snapshot

class DummyStageFail(IConsolidationStage):
    def execute(self, context, snapshot):
        raise ValueError("Stage failed")
        
@pytest.fixture
def dummy_context():
    return ConsolidationExecutionContext(
        dataset_version=1,
        trend_snapshot_version=1,
        configuration=ConsolidationConfiguration(),
        metadata=ConsolidationMetadata(
            execution_start_timestamp=datetime.now(timezone.utc),
            pipeline_version="1.0"
        )
    )

@pytest.fixture
def empty_snapshot():
    return ConsolidationSnapshot(
        snapshot_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_version=1,
        config_hash="abc",
        business_fingerprint="xyz",
        fingerprint_algorithm_version=1
    )

def test_pipeline_execution(dummy_context, empty_snapshot):
    pipeline = ConsolidationPipeline([DummyStagePass(), DummyStagePass()])
    result = pipeline.execute(dummy_context, empty_snapshot)
    assert result == empty_snapshot
    
def test_pipeline_fail_fast(dummy_context, empty_snapshot):
    pipeline = ConsolidationPipeline([DummyStagePass(), DummyStageFail(), DummyStagePass()])
    with pytest.raises(ValueError, match="Stage failed"):
        pipeline.execute(dummy_context, empty_snapshot)
