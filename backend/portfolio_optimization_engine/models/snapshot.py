from pydantic import BaseModel
from backend.shared.snapshots.models import BaseSnapshot
from backend.portfolio_optimization_engine.models.optimization_models import OptimizationResult
from backend.portfolio_optimization_engine.models.references import ParentSnapshotReferences

class PortfolioOptimizationMetadata(BaseModel):
    """
    Institutional metadata capturing the operational aspects of optimization.
    """
    execution_id: str
    pipeline_version: str
    configuration_version: str
    engine_version: str

    model_config = {"frozen": True}

class PortfolioOptimizationSnapshot(BaseSnapshot):
    """
    The final, deterministic, immutable portfolio optimization snapshot.
    """
    configuration_snapshot_id: str
    business_fingerprint: str
    
    optimization_result: OptimizationResult
    parent_snapshot_references: ParentSnapshotReferences
    optimization_metadata: PortfolioOptimizationMetadata

    model_config = {"frozen": True}
