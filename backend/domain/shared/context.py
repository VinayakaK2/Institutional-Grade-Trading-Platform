"""
Shared Execution Contexts
Provides domain models for passing request/audit metadata through the layers.
"""
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone
from typing import Optional

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditContext(BaseModel):
    """Context for auditing actions (e.g., who did what, when)."""
    user_id: str = "system"  # Replaced in later phases
    action_type: str
    timestamp: datetime = Field(default_factory=_utc_now)

class ExecutionContext(BaseModel):
    """Context for tracking execution flow (correlation IDs)."""
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "system"
    audit: Optional[AuditContext] = None

    @classmethod
    def create_system_context(cls, source: str = "system") -> "ExecutionContext":
        return cls(source=source)
