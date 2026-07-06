"""
Event Publisher Interface
"""
from backend.infrastructure.event_bus.models import BaseEvent
from backend.infrastructure.event_bus.bus import event_bus

class EventPublisher:
    """Helper class to publish events to the global bus."""
    
    @staticmethod
    async def publish(event: BaseEvent) -> None:
        """Publishes the given event."""
        await event_bus.publish(event)
