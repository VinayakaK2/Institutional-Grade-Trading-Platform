"""
Candle Storage Engine
Orchestrates business logic around storing candle datasets.
"""
from typing import List
import logging

from backend.candle_storage.contracts.engine import CandleStorageEngineContract
from backend.candle_storage.contracts.repository import CandleRepositoryContract
from backend.candle_storage.models.dataset import DatasetType
from backend.candle_storage.exceptions import CandleStorageException
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle

logger = logging.getLogger(__name__)

class CandleStorageEngine(CandleStorageEngineContract):
    """
    Implements storage logic, validating inputs before passing to the repository.
    The unit of work must be managed externally (via dependency injection) to 
    maintain transaction safety across batch operations.
    """
    def __init__(self, repository: CandleRepositoryContract):
        self._repository = repository
        
    def _validate_raw_candles(self, candles: List[RawCandle]):
        for idx, c in enumerate(candles):
            if not c.provider or not c.symbol or not c.timeframe or not c.raw_timestamp:
                raise CandleStorageException(f"Invalid RawCandle at index {idx}: missing required fields.")
                
    def _validate_normalized_candles(self, candles: List[Candle]):
        for idx, c in enumerate(candles):
            if not c.symbol or not c.timeframe or not c.timestamp:
                raise CandleStorageException(f"Invalid Candle at index {idx}: missing required fields.")
            
    async def save_raw_candles(self, candles: List[RawCandle]) -> None:
        """
        Validates and saves a batch of Raw candles.
        """
        if not candles:
            return
            
        self._validate_raw_candles(candles)
        await self._repository.save_batch(
            dataset_type=DatasetType.RAW,
            dataset_version=None,
            candles=candles
        )
        logger.info(f"Saved {len(candles)} raw candles.")

    async def save_canonical_candles(self, candles: List[Candle]) -> None:
        """
        Validates and saves a batch of Canonical candles.
        """
        if not candles:
            return
            
        self._validate_normalized_candles(candles)
        await self._repository.save_batch(
            dataset_type=DatasetType.CANONICAL,
            dataset_version=None,
            candles=candles
        )
        logger.info(f"Saved {len(candles)} canonical candles.")

    async def save_adjusted_candles(self, dataset_version: str, candles: List[Candle]) -> None:
        """
        Validates and saves a batch of Adjusted candles against a specific version.
        """
        if not candles:
            return
            
        if not dataset_version:
            raise CandleStorageException("dataset_version is required to save adjusted candles.")
            
        self._validate_normalized_candles(candles)
        await self._repository.save_batch(
            dataset_type=DatasetType.ADJUSTED,
            dataset_version=dataset_version,
            candles=candles
        )
        logger.info(f"Saved {len(candles)} adjusted candles for version {dataset_version}.")
