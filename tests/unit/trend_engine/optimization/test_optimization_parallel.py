import pytest
import asyncio
from backend.trend_engine.optimization.engine.parallel import AsyncBatchExecutor

@pytest.mark.asyncio
async def test_parallel_execution_preserves_order():
    executor = AsyncBatchExecutor()
    
    # Inputs
    items = [1, 2, 3, 4, 5]
    
    # Task that sleeps inversely proportional to its value
    # Item 5 sleeps 0.01s (finishes first)
    # Item 1 sleeps 0.05s (finishes last)
    async def process_item(item: int) -> str:
        sleep_time = (6 - item) * 0.01
        await asyncio.sleep(sleep_time)
        return f"result_{item}"
        
    results = await executor.execute_in_parallel(items, process_item, worker_count=5, batch_size=5)
    
    # Assert ordering is exactly as inputs
    assert results == ["result_1", "result_2", "result_3", "result_4", "result_5"]
