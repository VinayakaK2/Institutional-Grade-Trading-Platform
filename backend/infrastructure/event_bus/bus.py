"""
Event Bus Registry and Dispatcher
"""
import asyncio
from typing import Dict, List, Type
from collections import defaultdict

from backend.infrastructure.event_bus.models import BaseEvent
from backend.infrastructure.event_bus.subscriber import EventHandler
from backend.infrastructure.event_bus.exceptions import EventDispatchException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class EventBus:
    """
    Internal asynchronous Event Bus.
    Handles registering subscribers and dispatching events.
    """
    
    def __init__(self):
        # Maps Event class name to a list of handler instances
        self._registry: Dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        """Registers a handler for a specific event type."""
        event_name = event_type.__name__
        if handler not in self._registry[event_name]:
            self._registry[event_name].append(handler)
            logger.info(f"Registered handler {handler.__class__.__name__} for event {event_name}")

    async def publish(self, event: BaseEvent) -> None:
        """
        Dispatches an event to all registered handlers asynchronously.
        Failures in one handler do not prevent others from executing.
        """
        event_name = event.event_name
        handlers = self._registry.get(event_name, [])
        
        if not handlers:
            logger.debug(f"No handlers registered for event: {event_name}")
            return

        logger.info(f"Publishing event {event_name} to {len(handlers)} handlers", 
                    event_id=event.event_id, correlation_id=event.correlation_id)

        # Create tasks for all handlers to run concurrently
        tasks = [
            self._execute_handler(handler, event)
            for handler in handlers
        ]
        
        # Wait for all handlers to finish (or fail)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log failures
        for handler, result in zip(handlers, results):
            if isinstance(result, Exception):
                logger.error(
                    f"Handler {handler.__class__.__name__} failed processing {event_name}",
                    event_id=event.event_id,
                    exc_info=result
                )

    async def _execute_handler(self, handler: EventHandler, event: BaseEvent) -> None:
        """Wraps handler execution for safety."""
        # Timeout safety can be implemented here (e.g. asyncio.wait_for)
        try:
            await handler.handle(event)
        except Exception as e:
            raise EventDispatchException(f"Handler {handler.__class__.__name__} failed.", {"error": str(e)}) from e

# Global Event Bus Instance
event_bus = EventBus()
