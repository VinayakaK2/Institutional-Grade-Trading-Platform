"""
Historical Download Pipeline
"""
import logging
from typing import List, AsyncGenerator
from backend.historical_data.contracts.storage import HistoricalStorageContract
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.historical_data.engine.normalizer import DataNormalizer

logger = logging.getLogger(__name__)

class DownloadPipeline:
    """
    Coordinates the pipeline:
    Provider ➔ Raw Storage ➔ Normalization ➔ Normalized Storage
    """
    def __init__(self, storage: HistoricalStorageContract, batch_size: int = 5000):
        self._storage = storage
        self._batch_size = batch_size

    async def process_stream(self, stream: AsyncGenerator[RawCandle, None]) -> int:
        """
        Consumes the stream from a provider, batches writes to storage,
        normalizes the data, and persists it. Returns the number of saved records.
        """
        raw_buffer: List[RawCandle] = []
        saved_count = 0
        
        async for raw_candle in stream:
            raw_buffer.append(raw_candle)
            
            if len(raw_buffer) >= self._batch_size:
                await self._flush(raw_buffer)
                saved_count += len(raw_buffer)
                raw_buffer.clear()
                
        # Flush remaining
        if raw_buffer:
            await self._flush(raw_buffer)
            saved_count += len(raw_buffer)
            
        return saved_count
            
    async def _flush(self, raw_buffer: List[RawCandle]) -> None:
        """
        Executes the transactional boundaries. 
        Note: The storage adapter operates idempotently.
        """
        # 1. Save Raw (Download Pipeline ONLY saves raw data now)
        await self._storage.save_raw_candles(raw_buffer)

    @property
    def storage(self) -> HistoricalStorageContract:
        return self._storage
        
    async def replay_raw_data(self, symbol, timeframe, start, end) -> int:
        """
        Fetches raw candles from storage and re-runs them through the pipeline.
        Since canonical conversion is moved to Certification, this function here 
        could either be removed or just fetch the raw data stream.
        We'll just return the count of raw candles for now.
        """
        stream = self._storage.get_raw_candles(symbol, timeframe, start, end)
        
        count = 0
        async for _ in stream:
            count += 1
            
        return count
