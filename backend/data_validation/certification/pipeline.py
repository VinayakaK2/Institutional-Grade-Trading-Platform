from typing import List, AsyncGenerator
import logging

from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.historical_data.contracts.storage import HistoricalStorageContract
from backend.data_validation.contracts.storage import QuarantineStorageContract
from backend.data_validation.validation.engine import ValidationEngine
from backend.data_validation.cleaning.engine import CleaningEngine
from backend.data_validation.contracts.rule import ValidationContext
from backend.historical_data.engine.normalizer import DataNormalizer
from backend.historical_data.exceptions import NormalizationException

logger = logging.getLogger(__name__)

class CertificationPipeline:
    """
    Orchestrates the lifecycle from UNVALIDATED Raw Data 
    to CERTIFIED Canonical Data (or QUARANTINED Data).
    """
    def __init__(
        self, 
        storage: HistoricalStorageContract, 
        quarantine_storage: QuarantineStorageContract,
        validation_engine: ValidationEngine,
        cleaning_engine: CleaningEngine,
        batch_size: int = 5000
    ):
        self._storage = storage
        self._quarantine = quarantine_storage
        self._validation_engine = validation_engine
        self._cleaning_engine = cleaning_engine
        self._batch_size = batch_size

    async def process_stream(self, stream: AsyncGenerator[RawCandle, None], context: ValidationContext) -> int:
        """
        Consumes UNVALIDATED Raw Candles, validates, cleans, and saves CERTIFIED 
        Candles to canonical storage, while routing invalid to Quarantine.
        Returns the number of CERTIFIED canonical records saved.
        """
        raw_buffer: List[RawCandle] = []
        certified_count = 0
        
        async for raw_candle in stream:
            raw_buffer.append(raw_candle)
            
            if len(raw_buffer) >= self._batch_size:
                certified_count += await self._certify_batch(raw_buffer, context)
                raw_buffer.clear()
                
        if raw_buffer:
            certified_count += await self._certify_batch(raw_buffer, context)
            
        return certified_count

    async def _certify_batch(self, batch: List[RawCandle], context: ValidationContext) -> int:
        # 1. Validate
        validation_report = await self._validation_engine.run(context, batch)
        
        # 2. Clean and partition
        cleaning_result = await self._cleaning_engine.run(batch, validation_report)
        
        # 3. Quarantine rejected data
        if cleaning_result.rejected_records:
            await self._quarantine.save_quarantined_candles(
                cleaning_result.rejected_records, 
                reason="Failed certification (Validation/Cleaning)"
            )
            
        # 4. Canonical Conversion (Only cleaned, valid data)
        canonical_buffer: List[Candle] = []
        for raw in cleaning_result.cleaned_records:
            try:
                canonical = DataNormalizer.normalize(raw)
                canonical_buffer.append(canonical)
            except NormalizationException as e:
                # Should be rare since it passed structural validation
                logger.warning(f"Canonical conversion failed during certification: {e}")
                await self._quarantine.save_quarantined_candles([raw], reason=f"Canonical conversion failed: {e}")
                
        # 5. Persist to Canonical Storage
        if canonical_buffer:
            await self._storage.save_normalized_candles(canonical_buffer)
            
        return len(canonical_buffer)
