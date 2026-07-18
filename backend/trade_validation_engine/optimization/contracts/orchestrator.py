import abc
from typing import List, Coroutine, Any

class IExecutionOrchestrator(abc.ABC):
    """
    Abstract generic executor defining how tasks are executed.
    Future implementations may include DistributedExecutionOrchestrator or ThreadPoolExecutionOrchestrator.
    """
    @abc.abstractmethod
    async def execute(self, tasks: List[Coroutine[Any, Any, Any]], concurrency_limit: int, fail_fast: bool) -> List[Any]:
        """
        Executes a list of coroutine tasks asynchronously.
        
        Args:
            tasks: List of awaitable coroutines.
            concurrency_limit: Maximum number of concurrent tasks.
            fail_fast: If True, cancel remaining tasks and raise upon first exception.
        
        Returns:
            List of execution results matching the order of the tasks.
        """
        pass
