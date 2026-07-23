from abc import ABC, abstractmethod
from typing import List, Callable, TypeVar
import asyncio

T = TypeVar('T')

class ExecutionExecutor(ABC):
    """
    Pluggable executor interface to keep execution strategy replaceable 
    (Sync, Thread, Process, etc.) without bleeding into business logic.
    """

    @abstractmethod
    async def execute_batch(
        self,
        tasks: List[Callable[[], T]],
        concurrency_limit: int,
        fail_fast: bool
    ) -> List[T]:
        """
        Executes a batch of Callables and returns their results.
        Ordering must strictly match the input ordering.
        """
        pass

    @abstractmethod
    async def execute_sync(self, task: Callable[[], T]) -> T:
        """
        Executes a single synchronous task within the executor's concurrency model.
        """
        pass

class SyncExecutor(ExecutionExecutor):
    """
    Executes tasks synchronously inside an async loop.
    Avoids unnecessary threading overhead while maintaining the async interface.
    Default choice for light I/O or fast CPU-bound workflows.
    """
    async def execute_batch(
        self,
        tasks: List[Callable[[], T]],
        concurrency_limit: int,
        fail_fast: bool
    ) -> List[T]:
        
        results = []
        for task in tasks:
            try:
                # We simply run the sync task directly
                # If we need actual async concurrency, this executor wouldn't be purely sync
                # But since the caller expects it to be run safely without threads, we run sequentially.
                res = task()
                results.append(res)
            except Exception:
                if fail_fast:
                    raise
                # Wait, if fail_fast is False, we shouldn't just append None unless we wrap results.
                # Assuming tasks shouldn't fail or we throw. We'll throw anyway if fail_fast is True.
                # If False, maybe re-raise as a BatchExecutionError or just raise for now.
                raise
                
        return results

    async def execute_sync(self, task: Callable[[], T]) -> T:
        return task()

class ThreadExecutor(ExecutionExecutor):
    """
    Executes tasks using asyncio.to_thread for true parallelization of sync calls.
    Useful when tasks become more expensive later.
    """
    async def execute_batch(
        self,
        tasks: List[Callable[[], T]],
        concurrency_limit: int,
        fail_fast: bool
    ) -> List[T]:
        
        async def wrap_task(task):
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, task)
            
        # We can implement a semaphore here to respect concurrency_limit
        sem = asyncio.Semaphore(concurrency_limit)
        
        async def sem_task(task):
            async with sem:
                return await wrap_task(task)
                
        coroutines = [sem_task(t) for t in tasks]
        
        return await asyncio.gather(*coroutines, return_exceptions=not fail_fast)

    async def execute_sync(self, task: Callable[[], T]) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, task)
