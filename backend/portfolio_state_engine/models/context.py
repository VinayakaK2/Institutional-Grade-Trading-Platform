from typing import List, Dict
from pydantic import BaseModel, Field
from backend.portfolio_state_engine.models.state import OpenPosition, PendingOrder, CapitalSummary, PortfolioState
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioStateExecutionContext(BaseModel):
    """
    The immutable external API context containing fully prepared inputs.
    No data providers or unstructured raw dicts.
    """
    positions: List[OpenPosition]
    pending_orders: List[PendingOrder]
    capital: CapitalSummary
    realized_pnl: float
    unrealized_pnl: float
    parent_snapshot_references: ParentSnapshotReferences
    dataset_version: str
    configuration: PortfolioConfiguration
    
    model_config = {"frozen": True}

class PortfolioStatePipelineContext(BaseModel):
    """
    Internal context passed through the pipeline. Wraps execution context and holds 
    the assembled portfolio state.
    """
    execution_context: PortfolioStateExecutionContext
    execution_id: str
    portfolio_state: PortfolioState = Field(default_factory=PortfolioState)
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
