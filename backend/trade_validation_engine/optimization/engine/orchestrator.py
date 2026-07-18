import asyncio
from typing import List, Coroutine, Any
from backend.trade_validation_engine.optimization.contracts.orchestrator import IExecutionOrchestrator
from backend.trade_validation_engine.optimization.exceptions.exceptions import OptimizationConcurrencyError

class AsyncExecutionOrchestrator(IExecutionOrchestrator):
    """
    Runs generic tasks in parallel using asyncio.Semaphore based on config limits.
    """
    
    async def execute(self, tasks: List[Coroutine[Any, Any, Any]], concurrency_limit: int, fail_fast: bool) -> List[Any]:
        if not tasks:
            return []
            
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def bounded_task(task: Coroutine[Any, Any, Any]) -> Any:
            async with semaphore:
                return await task
                
        bounded_tasks = [bounded_task(t) for t in tasks]
        
        try:
            # return_exceptions = not fail_fast
            results = await asyncio.gather(*bounded_tasks, return_exceptions=not fail_fast)
            
            # If we didn't fail fast, we must raise any exceptions found inside the result list manually if we want them to bubble.
            # But the requirement states fail_fast=true means we cancel remaining and discard partial.
            # return_exceptions=False in gather means it will immediately raise the first exception, cancelling the others inherently.
            
            return results
        except Exception as e:
            raise OptimizationConcurrencyError(f"Parallel execution failed: {str(e)}") from e
