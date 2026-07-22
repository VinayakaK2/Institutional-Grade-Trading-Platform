from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class CandidatePositionSnapshot(BaseModel):
    """
    Immutable snapshot representing the candidate trade intent independently 
    of the Risk Engine.
    """
    snapshot_id: str
    symbol: str
    instrument: str
    exchange: str
    asset_class: str
    sector: str
    industry: str
    strategy_identifier: str
    direction: str
    entry_type: str
    intended_quantity: Optional[float] = None
    signal_identifier: str
    trade_identifier: str
    dataset_version: str
    configuration_version: str
    business_fingerprint: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"frozen": True}
