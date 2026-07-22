from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.portfolio_optimization_engine.models.configuration import PortfolioOptimizationConfiguration
from backend.portfolio_optimization_engine.models.optimization_models import OptimizationResult

from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot

class PortfolioOptimizationExecutionContext(BaseModel):
    """
    Immutable input payload for the Portfolio Optimization Engine.
    """
    portfolio_state_snapshot: PortfolioStateSnapshot
    portfolio_exposure_snapshot: PortfolioExposureSnapshot
    portfolio_correlation_snapshot: PortfolioCorrelationSnapshot
    portfolio_decision_snapshot: PortfolioDecisionSnapshot
    configuration: PortfolioOptimizationConfiguration
    dataset_version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

class PortfolioOptimizationPipelineContext(BaseModel):
    """
    Mutable context restricted strictly to pipeline stages.
    """
    execution_context: PortfolioOptimizationExecutionContext
    execution_id: str
    optimization_result: Optional[OptimizationResult] = None
    aggregated_facts: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}
