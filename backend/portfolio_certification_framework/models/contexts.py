from pydantic import BaseModel, Field
from typing import List
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult

class PortfolioCertificationExecutionContext(BaseModel):
    """
    The mutable context used during certification engine execution.
    Contains the input snapshot and accumulates certification results.
    """
    portfolio_optimization_snapshot: PortfolioOptimizationSnapshot
    dataset_version: str
    configuration_snapshot_id: str
    
    # Internal mutable state enriched by certification stages
    stage_results: List[CertificationStageResult] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
