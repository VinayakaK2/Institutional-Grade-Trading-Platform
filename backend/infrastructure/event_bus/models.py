"""
Event Models
Provides the base class for all internal events.
"""
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BaseEvent(BaseModel):
    """
    The root Base Event.
    All events published across the system must inherit from this.
    """
    # Standard Metadata
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the event")
    timestamp: datetime = Field(default_factory=_utc_now, description="UTC time the event occurred")
    source: str = Field(default="system", description="The component that generated the event")
    
    # Traceability
    correlation_id: Optional[str] = Field(default=None, description="Used to trace causality across async boundaries")

    @property
    def event_name(self) -> str:
        """Returns the class name of the event."""
        return self.__class__.__name__

    def payload(self) -> Dict[str, Any]:
        """Returns the event data as a dictionary."""
        return self.model_dump()
