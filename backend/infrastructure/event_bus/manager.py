"""
Event Bus Manager
Handles lifecycle of the event bus if external message brokers (RabbitMQ/Kafka) are introduced later.
Currently a placeholder for the in-memory bus lifecycle.
"""
from backend.core.logger import get_logger

logger = get_logger(__name__)

class EventBusManager:
    """Manages the Event Bus lifecycle."""
    
    @staticmethod
    async def startup() -> None:
        """Initializes Event Bus connections (if using external broker in Phase 1.2+)."""
        logger.info("Event Bus initialized (In-Memory).")

    @staticmethod
    async def shutdown() -> None:
        """Gracefully shuts down Event Bus processing."""
        logger.info("Event Bus shutdown.")
