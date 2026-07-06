"""
Download Manager
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

from backend.historical_data.models.metadata import DownloadRequest, DownloadMetadata, DownloadStatus
from backend.historical_data.providers.manager import ProviderManager
from backend.historical_data.engine.pipeline import DownloadPipeline
from backend.historical_data.exceptions import RateLimitException, ProviderUnavailableException

logger = logging.getLogger(__name__)

class DownloadManager:
    """
    Handles parallel execution, retries, and overall orchestration of historical data downloads.
    """
    def __init__(self, provider_manager: ProviderManager, pipeline: DownloadPipeline, max_concurrent: int = 5):
        self._provider_manager = provider_manager
        self._pipeline = pipeline
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._queue: asyncio.Queue[tuple] = asyncio.Queue()
        
        self._state: Dict[str, DownloadMetadata] = {}
        self._running = False
        self._workers: List[asyncio.Task] = []

    def start(self, worker_count: int = 3):
        """Starts background workers to process the download queue."""
        if self._running:
            return
        self._running = True
        for _ in range(worker_count):
            task = asyncio.create_task(self._worker_loop())
            self._workers.append(task)
            
    async def stop(self):
        """Gracefully shuts down the manager."""
        self._running = False
        for task in self._workers:
            task.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def enqueue(self, request: DownloadRequest) -> str:
        """Adds a request to the queue and returns its unique ID."""
        request_id = f"{request.symbol.symbol}_{request.timeframe.value}_{int(datetime.utcnow().timestamp())}"
        
        meta = DownloadMetadata(
            request_id=request_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            provider=request.provider or "auto",
            start_date=request.start_date,
            end_date=request.end_date
        )
        self._state[request_id] = meta
        
        # Enqueue as tuple (request, request_id)
        await self._queue.put((request, request_id))
        return request_id
        
    def get_status(self, request_id: str) -> Optional[DownloadMetadata]:
        return self._state.get(request_id)
        
    async def _worker_loop(self):
        while self._running:
            try:
                request, request_id = await self._queue.get()
            except asyncio.CancelledError:
                break
                
            async with self._semaphore:
                await self._process_request(request, request_id)
            self._queue.task_done()

    async def _process_request(self, request: DownloadRequest, request_id: str):
        meta = self._state[request_id]
        meta.status = DownloadStatus.IN_PROGRESS
        meta.updated_at = datetime.utcnow()
        
        start_time = datetime.utcnow()
        
        try:
            # Resolve Provider
            if request.provider and request.provider != "auto":
                provider = self._provider_manager.get_provider(request.provider)
                if not provider:
                    raise ProviderUnavailableException(request.provider, "Provider not registered")
            else:
                provider = await self._provider_manager.get_best_available_provider(request.timeframe)
                
            meta.provider = provider.name
            
            # Fetch Stream
            stream = provider.get_historical_data(
                request.symbol, request.timeframe, request.start_date, request.end_date
            )
            
            # Pipe to Storage
            saved_count = await self._pipeline.process_stream(stream)
            
            meta.records_saved = saved_count
            meta.status = DownloadStatus.COMPLETED
            meta.last_successful_sync = datetime.utcnow()
            
        except RateLimitException as e:
            logger.warning(f"Rate limit hit for {request_id}, sleeping {e.retry_after}s")
            meta.status = DownloadStatus.FAILED
            meta.failure_reason = str(e)
            
            if meta.retry_count < 3:
                await asyncio.sleep(e.retry_after)
                meta.retry_count += 1
                await self._queue.put((request, request_id))
            
        except Exception as e:
            logger.error(f"Download {request_id} failed: {e}", exc_info=True)
            meta.status = DownloadStatus.FAILED
            meta.failure_reason = str(e)
            
        finally:
            meta.updated_at = datetime.utcnow()
            meta.download_duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            try:
                await self._pipeline.storage.save_metadata(meta)
            except Exception as e:
                logger.error(f"Failed to persist metadata for {request_id}: {e}")
