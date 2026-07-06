"""
Scheduler Manager
Provides the global APScheduler AsyncIOScheduler instance and lifecycle methods.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobExecutionEvent

from backend.infrastructure.scheduler.config import scheduler_settings
from backend.infrastructure.scheduler.exceptions import SchedulerException
from backend.core.logger import get_logger

logger = get_logger(__name__)

# Global Scheduler Instance
scheduler = AsyncIOScheduler(
    timezone=scheduler_settings.scheduler_timezone,
    job_defaults={
        'coalesce': scheduler_settings.scheduler_coalesce,
        'max_instances': scheduler_settings.scheduler_max_instances,
        'misfire_grace_time': scheduler_settings.scheduler_misfire_grace_time,
    }
)

def _job_error_listener(event: JobExecutionEvent) -> None:
    """Listens for global job failures and logs them."""
    if event.exception:
        logger.error(
            f"Scheduled job {event.job_id} failed.",
            exc_info=event.exception,
            details={"job_id": event.job_id, "scheduled_run_time": str(event.scheduled_run_time)}
        )
    else:
        logger.warning(
            f"Scheduled job {event.job_id} missed execution.",
            details={"job_id": event.job_id, "scheduled_run_time": str(event.scheduled_run_time)}
        )

scheduler.add_listener(_job_error_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

class SchedulerManager:
    """Manages the Scheduler lifecycle."""
    
    @staticmethod
    async def startup() -> None:
        """Starts the scheduler in the background."""
        logger.info("Starting background job scheduler...")
        try:
            scheduler.start()
            logger.info("Scheduler started successfully.")
        except Exception as e:
            logger.critical("Failed to start scheduler.", exc_info=True)
            raise SchedulerException("Failed to start APScheduler.", {"error": str(e)}) from e

    @staticmethod
    async def shutdown() -> None:
        """Gracefully shuts down the scheduler."""
        logger.info("Shutting down scheduler...")
        try:
            scheduler.shutdown(wait=True)
            logger.info("Scheduler shut down successfully.")
        except Exception:
            logger.error("Error shutting down scheduler.", exc_info=True)
