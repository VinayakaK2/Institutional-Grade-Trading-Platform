import pytest
from backend.paper_execution_optimization_engine.executor.async_batch_executor import SyncExecutor, ThreadExecutor

@pytest.mark.asyncio
async def test_sync_executor_preserves_order():
    executor = SyncExecutor()
    
    def task1():
        return 1
    def task2():
        return 2
        
    tasks = [task1, task2]
    results = await executor.execute_batch(tasks, concurrency_limit=2, fail_fast=True)
    
    assert results == [1, 2]

@pytest.mark.asyncio
async def test_sync_executor_fail_fast():
    executor = SyncExecutor()
    
    def task1():
        raise ValueError("Task failed")
    
    tasks = [task1]
    with pytest.raises(ValueError, match="Task failed"):
        await executor.execute_batch(tasks, concurrency_limit=2, fail_fast=True)

@pytest.mark.asyncio
async def test_thread_executor_preserves_order():
    executor = ThreadExecutor()
    
    def task1():
        import time
        time.sleep(0.1)
        return 1
        
    def task2():
        return 2
        
    tasks = [task1, task2]
    results = await executor.execute_batch(tasks, concurrency_limit=2, fail_fast=True)
    
    # Task2 will finish first in thread pool, but results must preserve order
    assert results == [1, 2]
