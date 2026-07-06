"""
Event Subscriber Interface
"""
from typing import Protocol
from backend.infrastructure.event_bus.models import BaseEvent

class EventHandler(Protocol):
    """
    Protocol defining the structure of an Event Handler.
    Subscribers must implement this to receive events.
    """
    
    async def handle(self, event: BaseEvent) -> None:
        """Processes the received event."""
        ...
