from typing import Optional
from pydantic import BaseModel, Field
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.portfolio_correlation_engine.models.candidate import CandidatePositionSnapshot
from backend.portfolio_decision_engine.models.configuration import PortfolioDecisionConfigurationSnapshot
from backend.portfolio_decision_engine.models.decision_models import PortfolioDecision

class PortfolioDecisionExecutionContext(BaseModel):
    """
    Immutable input payload provided to the Portfolio Decision Engine.
    """
    portfolio_state_snapshot: PortfolioStateSnapshot
    portfolio_exposure_snapshot: PortfolioExposureSnapshot
    portfolio_correlation_snapshot: PortfolioCorrelationSnapshot
    risk_decision_snapshot: RiskDecisionSnapshot
    candidate_position_snapshot: CandidatePositionSnapshot
    configuration: PortfolioDecisionConfigurationSnapshot
    
    model_config = {"frozen": True}

class PortfolioDecisionPipelineContext(BaseModel):
    """
    Mutable state wrapper passed through the pipeline stages.
    """
    execution_context: PortfolioDecisionExecutionContext
    execution_id: str
    
    decision: Optional[PortfolioDecision] = None
    aggregated_facts: dict = Field(default_factory=dict)
