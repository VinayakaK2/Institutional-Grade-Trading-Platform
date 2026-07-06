"""
Historical Data Service Facade
"""
from typing import Optional
from datetime import datetime
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.engine.manager import DownloadManager
from backend.historical_data.models.metadata import DownloadRequest, DownloadMetadata

class HistoricalDataService:
    """
    Facade for the Historical Data Pipeline.
    Used by downstream services to trigger and monitor downloads.
    """
    def __init__(self, manager: DownloadManager):
        self._manager = manager
        
    def start_pipeline(self, workers: int = 3):
        self._manager.start(workers)
        
    async def stop_pipeline(self):
        await self._manager.stop()
        
    async def request_download(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start_date: datetime, 
        end_date: datetime,
        provider: Optional[str] = None,
        priority: int = 1
    ) -> str:
        """
        Enqueues a historical data download.
        Returns the unique request_id.
        """
        req = DownloadRequest(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            priority=priority
        )
        return await self._manager.enqueue(req)
        
    def get_download_status(self, request_id: str) -> Optional[DownloadMetadata]:
        """
        Returns the metadata and status for a specific download request.
        """
        return self._manager.get_status(request_id)
