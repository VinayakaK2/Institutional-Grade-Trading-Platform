from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from backend.corporate_actions.models.adjustment import AdjustmentMode

class DatasetVersion(BaseModel):
    """Tracks the version and adjustments applied to a canonical dataset."""
    original_version: str = Field(..., description="Hash or identifier of the original canonical dataset")
    adjusted_version: str = Field(..., description="Hash or identifier of the resulting adjusted dataset")
    applied_action_ids: List[str] = Field(default_factory=list, description="List of corporate action IDs applied")
    adjustment_mode: AdjustmentMode = Field(..., description="The mode used for adjustment")
    adjustment_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the adjustment was applied")
    
class AuditLog(BaseModel):
    """Immutable record tracking operator/system changes to corporate actions."""
    action_id: str = Field(..., description="ID of the action being modified/applied")
    operator: str = Field(default="SYSTEM", description="Identity of the operator or system")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of the audit event")
    event_type: str = Field(..., description="Type of event (e.g., CREATED, VALIDATED, APPLIED, REJECTED)")
    details: str = Field(default="", description="Additional details or rejection reasons")
