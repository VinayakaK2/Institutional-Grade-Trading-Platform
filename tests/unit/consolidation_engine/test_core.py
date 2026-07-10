import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.engine.core import ConsolidationEngineCore
from backend.consolidation_engine.pipeline.pipeline import ConsolidationPipeline
from backend.consolidation_engine.pipeline.stages.base import IConsolidationStage
from backend.consolidation_engine.config.config import ConsolidationConfiguration
from backend.consolidation_engine.repository.memory import InMemoryConsolidationRepository
from backend.consolidation_engine.models.fingerprint import BusinessFingerprint

class DummyStagePass(IConsolidationStage):
    def execute(self, context, snapshot):
        return snapshot

@pytest.mark.asyncio
async def test_engine_core_process():
    repo = InMemoryConsolidationRepository()
    pipeline = ConsolidationPipeline([DummyStagePass()])
    config = ConsolidationConfiguration()
    
    engine = ConsolidationEngineCore(repository=repo, pipeline=pipeline, config=config)
    
    base_fingerprint = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc",
        engine_version="1.0"
    )
    
    snapshot = await engine.process(dataset_version=1, trend_snapshot_version=1, base_fingerprint=base_fingerprint)
    
    assert snapshot.snapshot_version == 1
    assert snapshot.parent_dataset_version == 1
    assert snapshot.parent_trend_snapshot_version == 1
    
    saved_snapshot = await repo.load_latest_snapshot()
    assert saved_snapshot == snapshot

@pytest.mark.asyncio
async def test_engine_core_determinism():
    repo1 = InMemoryConsolidationRepository()
    pipeline1 = ConsolidationPipeline([DummyStagePass()])
    config1 = ConsolidationConfiguration()
    
    engine1 = ConsolidationEngineCore(repository=repo1, pipeline=pipeline1, config=config1)
    
    repo2 = InMemoryConsolidationRepository()
    pipeline2 = ConsolidationPipeline([DummyStagePass()])
    config2 = ConsolidationConfiguration()
    
    engine2 = ConsolidationEngineCore(repository=repo2, pipeline=pipeline2, config=config2)
    
    base_fingerprint = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc",
        engine_version="1.0"
    )
    
    snap1 = await engine1.process(1, 1, base_fingerprint)
    snap2 = await engine2.process(1, 1, base_fingerprint)
    
    # Exclude created_timestamp from comparison
    d1 = snap1.model_dump(exclude={"created_timestamp"})
    d2 = snap2.model_dump(exclude={"created_timestamp"})
    
    assert d1 == d2
