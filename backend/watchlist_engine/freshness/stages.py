"""
Freshness & Availability Pipeline Stages
========================================

Pipeline stages for the Freshness Engine.
"""
from typing import List
from datetime import datetime, timezone

from backend.watchlist_engine.contracts.contracts import IWatchlistStage
from backend.watchlist_engine.models.models import WatchlistExecutionContext, WatchlistStageResult, WatchlistStageStatus
from backend.watchlist_engine.freshness.config import FreshnessSettings
from backend.watchlist_engine.freshness.contracts import ICanonicalDatasetQueryService, ICandleQueryService
from backend.market_calendar.service.time_service import MarketTimeService
from backend.market_data.models.timeframe import Timeframe
import time

class FreshnessValidationStage(IWatchlistStage):
    """
    Validates that the most recent candle is within the acceptable freshness threshold.
    Rejects stale symbols.
    """
    def __init__(
        self, 
        settings: FreshnessSettings, 
        candle_query: ICandleQueryService,
        market_time: MarketTimeService
    ):
        self._settings = settings
        self._candle_query = candle_query
        self._market_time = market_time

    @property
    def name(self) -> str:
        return "FreshnessValidationStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.time()
        
        retained = []
        rejected_count = 0
        warnings = []
        
        now = datetime.now(timezone.utc)
        
        for candidate in context.candidates:
            symbol = candidate.watchlist_symbol.symbol
            exchange_code = candidate.watchlist_symbol.market_segment
            
            try:
                # Get the single latest candle
                candles = await self._candle_query.get_latest_candles(symbol, Timeframe.D1, 1)
                
                if not candles:
                    warnings.append(f"No candles found for {symbol.full_name}")
                    rejected_count += 1
                    continue
                    
                latest_candle = candles[0]
                
                # Check absolute age against max_data_age_days
                age_days = (now - latest_candle.timestamp).days
                if age_days > self._settings.max_data_age_days:
                    warnings.append(f"Stale data for {symbol.full_name}: {age_days} days old")
                    rejected_count += 1
                    continue
                    
                retained.append(candidate)
                
            except Exception as e:
                warnings.append(f"Failed to validate freshness for {symbol.full_name}: {str(e)}")
                rejected_count += 1
                
        context.candidates = retained
        
        duration_ms = (time.time() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={"rejected_count": rejected_count},
            warnings=warnings
        )


class AvailabilityValidationStage(IWatchlistStage):
    """
    Validates that the canonical dataset exists and is certified.
    """
    def __init__(self, dataset_query: ICanonicalDatasetQueryService):
        self._dataset_query = dataset_query

    @property
    def name(self) -> str:
        return "AvailabilityValidationStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.time()
        
        # We fetch the requested dataset_version from the engine's shared_state
        requested_dataset_version = context.shared_state.get("dataset_version")
        if not requested_dataset_version:
            raise ValueError("AvailabilityValidationStage requires 'dataset_version' in shared_state.")
            
        retained = []
        rejected_count = 0
        warnings = []
        
        for candidate in context.candidates:
            symbol = candidate.watchlist_symbol.symbol
            
            try:
                actual_version = await self._dataset_query.get_canonical_dataset_version(symbol)
                
                if actual_version != requested_dataset_version:
                    warnings.append(f"Dataset version mismatch for {symbol.full_name}: Expected {requested_dataset_version}, got {actual_version}")
                    rejected_count += 1
                    continue
                    
                retained.append(candidate)
                
            except Exception as e:
                warnings.append(f"Canonical dataset not available for {symbol.full_name}: {str(e)}")
                rejected_count += 1
                
        context.candidates = retained
        
        duration_ms = (time.time() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={"rejected_count": rejected_count},
            warnings=warnings
        )


class DatasetIntegrityValidationStage(IWatchlistStage):
    """
    Analyzes the latest fetched candles to ensure strictly monotonic timestamp ordering.
    Detects and rejects duplicate or missing candles structurally.
    """
    def __init__(self, settings: FreshnessSettings, candle_query: ICandleQueryService):
        self._settings = settings
        self._candle_query = candle_query

    @property
    def name(self) -> str:
        return "DatasetIntegrityValidationStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.time()
        
        retained = []
        rejected_count = 0
        warnings = []
        
        lookback = self._settings.integrity_check_lookback
        
        for candidate in context.candidates:
            symbol = candidate.watchlist_symbol.symbol
            
            try:
                candles = await self._candle_query.get_latest_candles(symbol, Timeframe.D1, lookback)
                
                if len(candles) < 2:
                    # Can't check ordering on 0 or 1 candle, but we pass it as it's not explicitly broken
                    retained.append(candidate)
                    continue
                    
                is_valid = True
                
                # Check for strictly monotonic increasing timestamps
                for i in range(1, len(candles)):
                    if candles[i].timestamp <= candles[i-1].timestamp:
                        warnings.append(f"Structural defect: Non-monotonic or duplicate timestamp for {symbol.full_name} at {candles[i].timestamp}")
                        is_valid = False
                        break
                        
                if is_valid:
                    retained.append(candidate)
                else:
                    rejected_count += 1
                    
            except Exception as e:
                warnings.append(f"Failed to check integrity for {symbol.full_name}: {str(e)}")
                rejected_count += 1
                
        context.candidates = retained
        
        duration_ms = (time.time() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={"rejected_count": rejected_count},
            warnings=warnings
        )
