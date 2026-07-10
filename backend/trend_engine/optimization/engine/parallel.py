import asyncio
from typing import List, Callable, Awaitable, TypeVar
import logging

from backend.trend_engine.optimization.contracts.contracts import IParallelExecutor

logger = logging.getLogger(__name__)

T_In = TypeVar('T_In')
T_Out = TypeVar('T_Out')

class AsyncBatchExecutor(IParallelExecutor):
    """
    Executes asynchronous tasks in parallel with a bounded concurrency limit.
    Guarantees that the returned list of results exactly matches the order
    of the input items, satisfying the deterministic merge contract.
    """
    
    async def execute_in_parallel(
        self, 
        items: List[T_In], 
        task_func: Callable[[T_In], Awaitable[T_Out]], 
        worker_count: int, 
        batch_size: int
    ) -> List[T_Out]:
        
        if not items:
            return []
            
        semaphore = asyncio.Semaphore(worker_count)
        
        async def bounded_task(item: T_In) -> T_Out:
            async with semaphore:
                return await task_func(item)
                
        # asyncio.gather strictly preserves the order of the passed awaitables 
        # in its return list, regardless of completion order.
        tasks = [bounded_task(item) for item in items]
        
        try:
            results = await asyncio.gather(*tasks)
            return list(results)
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            raise
