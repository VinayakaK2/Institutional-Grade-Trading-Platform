import time
from typing import List
from backend.universe_engine.contracts.pipeline import IUniverseStage
from backend.universe_engine.models.universe import (
    UniverseExecutionContext,
    StageResult,
    StageStatus,
    UniverseInstrument,
)
from backend.core.logger import get_logger

logger = get_logger(__name__)

class BaseFilterStage(IUniverseStage):
    """
    Base class for universe filtering stages.
    Provides common logic for filtering instruments and generating StageResult metrics.
    """
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, context: UniverseExecutionContext) -> StageResult:
        start_time = time.perf_counter()
        initial_count = len(context.instruments)
        
        # Keep instruments that pass the filter
        retained = []
        rejected_count = 0
        
        for inst in context.instruments:
            if self._is_eligible(inst):
                retained.append(inst)
            else:
                rejected_count += 1
                
        context.instruments = retained
        
        duration = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            f"Stage {self.name} completed. "
            f"Retained: {len(retained)}, Rejected: {rejected_count}."
        )
        
        return StageResult(
            stage_name=self.name,
            status=StageStatus.SUCCESS,
            duration_ms=duration,
            metadata={
                "initial_count": initial_count,
                "retained_count": len(retained),
                "rejected_count": rejected_count
            }
        )
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        """
        Determine if the instrument should be kept.
        Override this method in subclasses.
        """
        raise NotImplementedError


class ExchangeFilterStage(BaseFilterStage):
    def __init__(self, allowed_exchanges: List[str]):
        super().__init__("ExchangeFilterStage")
        self._allowed = set(allowed_exchanges)
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        return instrument.symbol.exchange.code in self._allowed


class MarketSegmentFilterStage(BaseFilterStage):
    def __init__(self, allowed_segments: List[str]):
        super().__init__("MarketSegmentFilterStage")
        self._allowed = set(allowed_segments)
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        return instrument.market_segment.value in self._allowed


class InstrumentTypeFilterStage(BaseFilterStage):
    def __init__(self, allowed_types: List[str]):
        super().__init__("InstrumentTypeFilterStage")
        self._allowed = set(allowed_types)
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        return instrument.instrument_type.value in self._allowed


class TradingStatusFilterStage(BaseFilterStage):
    def __init__(self, rejected_statuses: List[str]):
        super().__init__("TradingStatusFilterStage")
        self._rejected = set(rejected_statuses)
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        return instrument.trading_status.value not in self._rejected


class DelistedFilterStage(BaseFilterStage):
    def __init__(self, remove_delisted: bool):
        super().__init__("DelistedFilterStage")
        self._remove_delisted = remove_delisted
        
    def _is_eligible(self, instrument: UniverseInstrument) -> bool:
        if self._remove_delisted and instrument.is_delisted:
            return False
        return True
