"""
Job Registration and Pipeline
Helpers for defining and registering scheduled jobs.
"""
from typing import Callable, Coroutine, Any
from typing import Optional
from functools import wraps

from backend.infrastructure.scheduler.manager import scheduler
from backend.infrastructure.scheduler.exceptions import JobExecutionException
from backend.core.logger import get_logger

logger = get_logger(__name__)

def scheduled_job(cron_expression: str, job_id: Optional[str] = None) -> Callable:
    """
    Decorator to register a function as a cron-based scheduled job.
    Wraps the execution in our standard exception and logging pipeline.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable:
        name = job_id or func.__name__

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Executing scheduled job: {name}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Successfully completed scheduled job: {name}")
                return result
            except Exception as e:
                logger.error(f"Scheduled job {name} failed with an exception.", exc_info=True)
                # Translating domain/infra exceptions into JobExecutionException
                raise JobExecutionException(f"Job {name} failed.", {"error": str(e)}) from e
        
        # Parse simplified cron to apscheduler kwargs (assumes standard 5-part cron)
        # For a full production implementation, croniter or a custom parser is preferred.
        # Here we use APScheduler's CronTrigger interface.
        parts = cron_expression.split()
        if len(parts) == 5:
            trigger_kwargs = {
                "minute": parts[0],
                "hour": parts[1],
                "day": parts[2],
                "month": parts[3],
                "day_of_week": parts[4],
            }
            scheduler.add_job(wrapper, 'cron', id=name, replace_existing=True, **trigger_kwargs)
            logger.info(f"Registered scheduled job {name} with cron '{cron_expression}'")
        else:
            logger.error(f"Invalid cron expression for job {name}: {cron_expression}")
            
        return wrapper
    return decorator
