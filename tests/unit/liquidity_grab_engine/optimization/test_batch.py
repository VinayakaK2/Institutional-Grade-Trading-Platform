import pytest
import asyncio
from backend.liquidity_grab_engine.optimization.execution.batch import AsyncBatchExecutor

@pytest.mark.asyncio
async def test_async_batch_executor_maintains_order():
    executor = AsyncBatchExecutor(batch_size=2, max_parallelism=2)
    
    async def mock_task(item: int) -> int:
        await asyncio.sleep(0.01)
        return item * 2
        
    inputs = [1, 2, 3, 4, 5]
    results = await executor.execute_batch(inputs, mock_task)
    
    assert results == [2, 4, 6, 8, 10]
    
@pytest.mark.asyncio
async def test_async_batch_executor_sequential_equals_parallel():
    # Sequential (batch_size=1, max_parallelism=1)
    seq_executor = AsyncBatchExecutor(batch_size=1, max_parallelism=1)
    # Parallel (batch_size=10, max_parallelism=5)
    par_executor = AsyncBatchExecutor(batch_size=10, max_parallelism=5)
    
    async def mock_task(item: str) -> str:
        await asyncio.sleep(0.01)
        return item.upper()
        
    inputs = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
    
    seq_res = await seq_executor.execute_batch(inputs, mock_task)
    par_res = await par_executor.execute_batch(inputs, mock_task)
    
    assert seq_res == par_res
    
def test_async_batch_executor_invalid_params():
    with pytest.raises(ValueError):
        AsyncBatchExecutor(batch_size=0, max_parallelism=1)
        
    with pytest.raises(ValueError):
        AsyncBatchExecutor(batch_size=1, max_parallelism=0)
