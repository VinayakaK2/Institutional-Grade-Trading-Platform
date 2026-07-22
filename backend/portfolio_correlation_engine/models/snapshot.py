from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.portfolio_correlation_engine.models.correlation_models import PortfolioCorrelationAnalysis, CorrelationMetrics
from backend.portfolio_correlation_engine.models.references import ParentSnapshotReferences
from backend.shared.snapshots.models import BaseSnapshot

class PortfolioCorrelationSnapshot(BaseSnapshot):
    """
    The canonical immutable entity resulting from pipeline execution.
    Contains raw analysis, metrics, infrastructure metadata, lineage, and the hash.
    """
    correlation_analysis: PortfolioCorrelationAnalysis
    correlation_metrics: CorrelationMetrics
    parent_snapshot_references: ParentSnapshotReferences
    configuration_snapshot_id: str
    
    model_config = {"frozen": True}
