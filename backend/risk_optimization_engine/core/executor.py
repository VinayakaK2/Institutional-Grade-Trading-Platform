import asyncio
from typing import List, Callable, Awaitable, Any, Tuple

class AsyncBatchExecutor:
    """
    Manages parallel execution of async tasks with configurable workers and batch sizes.
    Ensures Ordered Merge.
    """
    def __init__(self, max_workers: int = 10, batch_size: int = 50, timeout: float = 30.0, retry: int = 0):
        self._max_workers = max_workers
        self._batch_size = batch_size
        self._timeout = timeout
        self._retry = retry
        
    async def execute_in_batches(self, items: List[Any], func: Callable[[Any], Awaitable[Any]]) -> List[Any]:
        """
        Executes a function across all items in parallel batches, preserving the original order.
        """
        if not items:
            return []
            
        # Add index to preserve order
        indexed_items = list(enumerate(items))
        results: List[Tuple[int, Any]] = []
        
        # Process in batches
        for i in range(0, len(indexed_items), self._batch_size):
            batch = indexed_items[i:i + self._batch_size]
            
            # Use a semaphore to limit concurrent workers
            sem = asyncio.Semaphore(self._max_workers)
            
            async def _execute_with_sem(idx: int, item: Any) -> Tuple[int, Any]:
                async with sem:
                    for attempt in range(self._retry + 1):
                        try:
                            # Apply timeout
                            res = await asyncio.wait_for(func(item), timeout=self._timeout)
                            return idx, res
                        except asyncio.TimeoutError:
                            if attempt == self._retry:
                                raise
                    raise RuntimeError("Should not reach here")
                                
            # We must return Tuple[int, Any] because mypy expects it based on definition, wait, if it fails it raises, 
            # so it always returns Tuple[int, Any] on success.
            
            batch_tasks = [_execute_with_sem(idx, item) for idx, item in batch]
            batch_results = await asyncio.gather(*batch_tasks) # type: ignore
            
            results.extend(batch_results)
            
        # Ordered Merge (Sort by original index)
        results.sort(key=lambda x: x[0])
        
        # Return only the results
        return [r[1] for r in results]
