"""
Background Task Manager
Manages long-running asyncio tasks, ensuring they are cancelled cleanly on shutdown.
"""
import asyncio
from typing import Set, Coroutine, Any
from backend.core.logger import get_logger

logger = get_logger(__name__)

class BackgroundTaskManager:
    """Tracks and cleanly shuts down background tasks."""
    
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()

    def create_task(self, coro: Coroutine[Any, Any, Any], name: str = None) -> asyncio.Task:
        """Registers a coroutine as a background task."""
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)
        
        # When the task completes, remove it from the tracking set
        task.add_done_callback(self._tasks.discard)
        logger.debug(f"Registered background task: {name or task.get_name()}")
        return task

    async def shutdown(self, timeout: float = 5.0) -> None:
        """Cancels all tracked tasks and waits for them to exit."""
        if not self._tasks:
            return
            
        logger.info(f"Cancelling {len(self._tasks)} background tasks...")
        for task in self._tasks:
            task.cancel()
            
        # Wait for all tasks to acknowledge cancellation
        results = await asyncio.gather(*self._tasks, return_exceptions=True)
        
        for task, result in zip(self._tasks, results):
            if isinstance(result, asyncio.CancelledError):
                logger.debug(f"Task {task.get_name()} cancelled successfully.")
            elif isinstance(result, Exception):
                logger.error(f"Task {task.get_name()} exited with error during shutdown.", exc_info=result)

# Global Task Manager
task_manager = BackgroundTaskManager()
