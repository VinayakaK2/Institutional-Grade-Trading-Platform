import asyncio
import logging
from typing import List, Awaitable, Callable, TypeVar

logger = logging.getLogger(__name__)

T_in = TypeVar('T_in')
T_out = TypeVar('T_out')

class AsyncBatchExecutor:
    """
    Executes tasks in parallel batches deterministically.
    Maintains input order for outputs.
    """
    
    def __init__(self, batch_size: int, max_parallelism: int) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if max_parallelism <= 0:
            raise ValueError("max_parallelism must be positive")
            
        self._batch_size = batch_size
        self._semaphore = asyncio.Semaphore(max_parallelism)
        
    async def _execute_task_with_semaphore(
        self, 
        task_func: Callable[[T_in], Awaitable[T_out]], 
        item: T_in
    ) -> T_out:
        """Executes a single task using the semaphore limit."""
        async with self._semaphore:
            return await task_func(item)
            
    async def execute_batch(
        self, 
        items: List[T_in], 
        task_func: Callable[[T_in], Awaitable[T_out]]
    ) -> List[T_out]:
        """
        Executes a list of items using the provided task_func in batches.
        Returns the output list in the exact same order as the items list.
        """
        logger.info(f"Executing batch of {len(items)} items with batch_size={self._batch_size}")
        
        all_results: List[T_out] = []
        
        # Process in chunks of batch_size
        for i in range(0, len(items), self._batch_size):
            chunk = items[i:i + self._batch_size]
            
            # Map chunk to coroutines
            coroutines = [
                self._execute_task_with_semaphore(task_func, item)
                for item in chunk
            ]
            
            # Gather chunk results (gather maintains order of coroutines passed)
            try:
                chunk_results = await asyncio.gather(*coroutines)
                all_results.extend(chunk_results)
            except Exception as e:
                logger.error(f"Error executing batch chunk {i} to {i + len(chunk)}: {str(e)}")
                raise
                
        return all_results
