from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.report import PortfolioRiskReport

class PortfolioRiskMetadata(BaseModel):
    execution_duration_ms: int = Field(description="Total execution time in milliseconds")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution info")
    
    model_config = {"frozen": True}

class PortfolioRiskSnapshot(BaseModel):
    """
    Immutable snapshot containing the finalized portfolio risk evaluation.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the snapshot")
    context: PortfolioRiskContext = Field(description="Execution context")
    report: PortfolioRiskReport = Field(description="Portfolio risk report containing evidence")
    metadata: PortfolioRiskMetadata = Field(description="Associated metadata (excluded from deterministic hashing)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    model_config = {"frozen": True}
