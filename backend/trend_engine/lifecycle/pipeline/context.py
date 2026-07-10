from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.trend_engine.lifecycle.config.config import TrendLifecycleConfig
from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.quality.models.models import TrendQualitySnapshot
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState, ContinuationEvidence, WeakeningEvidence, BreakEvidence, EndEvidence

class SymbolLifecycleContext(BaseModel):
    """Holds mutable intermediate state for a single symbol during pipeline execution."""
    symbol_key: str
    
    # Track the previous known state (if available) to validate transitions.
    # If no previous state exists, it starts as ACTIVE by default.
    previous_state: TrendLifecycleState = TrendLifecycleState.ACTIVE
    
    # Evidence outputs from individual stages
    continuation_evidence: Optional[ContinuationEvidence] = None
    weakening_evidence: Optional[WeakeningEvidence] = None
    break_evidence: Optional[BreakEvidence] = None
    end_evidence: Optional[EndEvidence] = None
    
    # Final resolved state from aggregation
    final_state: Optional[TrendLifecycleState] = None

class LifecycleExecutionContext(BaseModel):
    """
    Mutable context propagated through all pipeline stages.
    """
    config: TrendLifecycleConfig
    trend_snapshot: TrendSnapshot
    quality_snapshot: TrendQualitySnapshot
    
    # Previous lifecycle snapshot (optional, used for transitions)
    # We pass it in so stages can see previous state.
    # Note: To avoid circular imports we type this as Any or use TYPE_CHECKING.
    # Since it's not strictly required in the model validation, we can just use dict for now 
    # or strongly type it if we import it.
    
    symbol_contexts: Dict[str, SymbolLifecycleContext] = Field(default_factory=dict)
    
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
