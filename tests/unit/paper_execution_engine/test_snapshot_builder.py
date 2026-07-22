from backend.paper_execution_engine.builders.snapshot_builder import PaperExecutionSnapshotBuilder

def test_deterministic_hashing(dummy_context, dummy_pipeline_context):
    builder = PaperExecutionSnapshotBuilder()
    
    # Build two snapshots from the exact same inputs
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    snap2 = builder.build(dummy_context, dummy_pipeline_context)
    
    # Business fingerprint MUST be perfectly identical across identical builds
    assert snap1.business_fingerprint == snap2.business_fingerprint
    
    # Configuration hash MUST be identical
    assert snap1.configuration_hash == snap2.configuration_hash
    
    # Snapshot hashes and IDs SHOULD NOT match because timestamps/UUIDs differ
    assert snap1.snapshot_id != snap2.snapshot_id
    assert snap1.snapshot_hash != snap2.snapshot_hash
    
    # Snapshot version MUST match as it is deterministic based on business fingerprint
    assert snap1.snapshot_version == snap2.snapshot_version

def test_fingerprint_mutates_on_business_change(dummy_context, dummy_pipeline_context, dummy_configuration, dummy_metadata):
    from backend.paper_execution_engine.models.contexts import PaperExecutionContext
    builder = PaperExecutionSnapshotBuilder()
    
    snap1 = builder.build(dummy_context, dummy_pipeline_context)
    
    # Mutate a deterministic input (symbol)
    mutated_context = PaperExecutionContext(
        symbol="TSLA",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_v_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )
    
    snap2 = builder.build(mutated_context, dummy_pipeline_context)
    
    # Business fingerprint MUST mutate
    assert snap1.business_fingerprint != snap2.business_fingerprint
