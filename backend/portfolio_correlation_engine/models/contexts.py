from typing import Dict
from pydantic import BaseModel, Field
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.portfolio_correlation_engine.models.candidate import CandidatePositionSnapshot
from backend.portfolio_correlation_engine.models.configuration import PortfolioCorrelationConfigurationSnapshot
from backend.portfolio_correlation_engine.models.correlation_models import PortfolioCorrelationAnalysis, CorrelationMetrics

class PortfolioCorrelationExecutionContext(BaseModel):
    """
    The immutable external API context. Contains all required parent snapshots.
    """
    portfolio_state_snapshot: PortfolioStateSnapshot
    portfolio_exposure_snapshot: PortfolioExposureSnapshot
    candidate_position_snapshot: CandidatePositionSnapshot
    risk_decision_snapshot: RiskDecisionSnapshot
    configuration: PortfolioCorrelationConfigurationSnapshot
    
    model_config = {"frozen": True}

class PortfolioCorrelationPipelineContext(BaseModel):
    """
    Internal context wrapping the execution context. 
    Strictly write-only internally, must never leak outside the pipeline.
    """
    execution_context: PortfolioCorrelationExecutionContext
    execution_id: str
    correlation_analysis: PortfolioCorrelationAnalysis = Field(default_factory=PortfolioCorrelationAnalysis)
    correlation_metrics: CorrelationMetrics = Field(default_factory=CorrelationMetrics)
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
