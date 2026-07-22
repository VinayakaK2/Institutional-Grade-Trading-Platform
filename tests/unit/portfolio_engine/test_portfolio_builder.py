import pytest
from backend.portfolio_engine.builders.snapshot_builder import PortfolioSnapshotBuilder
from backend.portfolio_engine.models.references import ParentSnapshotReferences

def test_deterministic_snapshot_id():
    refs = ParentSnapshotReferences(risk_snapshot_version="v1.0")
    
    b1 = PortfolioSnapshotBuilder() \
        .with_dataset_version("v1.0") \
        .with_parent_snapshot_references(refs) \
        .with_configuration_hash("hash")
        
    b2 = PortfolioSnapshotBuilder() \
        .with_dataset_version("v1.0") \
        .with_parent_snapshot_references(refs) \
        .with_configuration_hash("hash")
        
    s1 = b1.build()
    s2 = b2.build()
    
    assert s1.snapshot_id == s2.snapshot_id
    
def test_builder_missing_data():
    b1 = PortfolioSnapshotBuilder()
    with pytest.raises(ValueError):
        b1.build()
