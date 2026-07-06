"""
Global Infrastructure Lifecycle Manager
Coordinates the startup and shutdown sequences for all infrastructure components.
"""
from backend.infrastructure.database.manager import DatabaseManager
from backend.infrastructure.redis.manager import RedisManager
from backend.infrastructure.event_bus.manager import EventBusManager
from backend.infrastructure.scheduler.manager import SchedulerManager
from backend.core.logger import get_logger

logger = get_logger(__name__)

class InfrastructureLifecycleManager:
    """Manages the startup and shutdown lifecycle of the entire infrastructure layer."""

    @staticmethod
    async def startup() -> None:
        """Starts all infrastructure components in the correct dependency order."""
        logger.info("Initiating global infrastructure startup sequence...")
        try:
            # 1. Database
            await DatabaseManager.startup()
            
            # 2. Cache / KV Store
            await RedisManager.startup()
            
            # 3. Message/Event Bus
            await EventBusManager.startup()
            
            # 4. Background Scheduler
            await SchedulerManager.startup()
            
            logger.info("Global infrastructure startup sequence completed successfully.")
        except Exception:
            logger.critical("Failed during infrastructure startup sequence. Halting application.", exc_info=True)
            # In a real app, this should trigger a hard exit (e.g. sys.exit(1)) so orchestrators can restart it.
            raise

    @staticmethod
    async def shutdown() -> None:
        """Shuts down all infrastructure components safely."""
        logger.info("Initiating global infrastructure shutdown sequence...")
        
        # Shut down in reverse dependency order
        
        # 1. Stop processing new background jobs
        await SchedulerManager.shutdown()
        
        # 2. Stop receiving/publishing events
        await EventBusManager.shutdown()
        
        # 3. Close Cache connections
        await RedisManager.shutdown()
        
        # 4. Close DB connections last to allow in-flight events/jobs to finish
        await DatabaseManager.shutdown()
        
        logger.info("Global infrastructure shutdown sequence completed.")
