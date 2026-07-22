from backend.paper_order_engine.builders.snapshot_builder import PaperOrderSnapshotBuilder

def test_deterministic_hashing(dummy_context, dummy_pipeline_context):
    builder = PaperOrderSnapshotBuilder()
    
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    snap2 = builder.build(dummy_context, dummy_pipeline_context)
    
    assert snap1.business_fingerprint == snap2.business_fingerprint
    assert snap1.snapshot_version == snap2.snapshot_version
    
    assert snap1.snapshot_id != snap2.snapshot_id
    assert snap1.snapshot_hash != snap2.snapshot_hash

def test_fingerprint_mutates_on_business_change(dummy_context, dummy_pipeline_context, dummy_metadata):
    from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext
    builder = PaperOrderSnapshotBuilder()
    
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    
    mutated_context = PaperOrderExecutionContext(
        symbol="TSLA",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration=dummy_context.configuration,
        metadata=dummy_metadata
    )
    
    snap2 = builder.build(mutated_context, dummy_pipeline_context)
    
    assert snap1.business_fingerprint != snap2.business_fingerprint
    assert snap1.snapshot_version != snap2.snapshot_version
