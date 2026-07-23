import pytest
from backend.paper_fill_engine.builders.snapshot_builder import PaperFillSnapshotBuilder
from backend.paper_fill_engine.core.stages import DeterministicFillStage
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext

@pytest.mark.asyncio
async def test_deterministic_hashing(dummy_context, dummy_pipeline_context):
    stage = DeterministicFillStage()
    await stage.execute(dummy_context, dummy_pipeline_context)
    
    builder = PaperFillSnapshotBuilder()
    
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    snap2 = builder.build(dummy_context, dummy_pipeline_context)
    
    # Fingerprint must be perfectly stable across same inputs
    assert snap1.business_fingerprint == snap2.business_fingerprint
    assert snap1.snapshot_version == snap2.snapshot_version
    
    # Hash is different because created_at and snapshot_id differ
    assert snap1.snapshot_id != snap2.snapshot_id
    assert snap1.snapshot_hash != snap2.snapshot_hash

@pytest.mark.asyncio
async def test_fingerprint_mutates_on_business_change(dummy_context, dummy_pipeline_context, dummy_metadata):
    stage = DeterministicFillStage()
    await stage.execute(dummy_context, dummy_pipeline_context)
    
    builder = PaperFillSnapshotBuilder()
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    
    mutated_context = PaperFillExecutionContext(
        symbol="TSLA",
        timeframe="1D",
        dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration=dummy_context.configuration,
        metadata=dummy_metadata
    )
    
    # Reset result
    dummy_pipeline_context.simulation_result = None
    await stage.execute(mutated_context, dummy_pipeline_context)
    
    snap2 = builder.build(mutated_context, dummy_pipeline_context)
    
    assert snap1.business_fingerprint != snap2.business_fingerprint
    assert snap1.snapshot_version != snap2.snapshot_version
