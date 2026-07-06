import uuid
from typing import List, Dict, Any
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent, VolumeEventType, CandleClassification
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig
from backend.volume_analysis_engine.contracts.analyzer import VolumeEventDetectorContract
import logging

logger = logging.getLogger(__name__)

class VolumeEventDetector(VolumeEventDetectorContract):
    """
    Detects volume events from historical candles based on configured RVOL thresholds.
    
    Threshold Comparison Rules:
    - EXPANSION: RVOL >= config.expansion_threshold
    - CONTRACTION: RVOL <= config.contraction_threshold
    - DRY VOLUME: RVOL <= config.dry_volume_threshold
    - CLIMAX: RVOL >= config.climax_threshold
    
    Consecutive Event Behaviour:
    The detector tracks consecutive occurrences of the same event state.
    If a candle meets the threshold, the counter increments.
    If a candle FAILS to meet the threshold, the counter instantly resets to 0.
    Example: 
        Expansion -> Expansion -> Expansion -> Normal Volume -> Counter Reset (0).
        
    Event Ordering:
    If multiple events are triggered on the exact same candle, they are always generated and appended in this deterministic order:
    1. CLIMAX
    2. EXPANSION
    3. DRY VOLUME
    4. CONTRACTION
    """
    def detect_events(
        self, 
        candles: List[Candle], 
        analysis_results: List[VolumeAnalysisResult], 
        config: VolumeAnalysisConfig,
        previous_events: List[VolumeEvent]
    ) -> List[VolumeEvent]:
        if not candles or not analysis_results:
            return []
            
        if len(candles) != len(analysis_results):
            raise ValueError(f"Candles ({len(candles)}) and Results ({len(analysis_results)}) length mismatch")

        events = []
        
        # Initialize consecutive counters from previous events
        consecutive_expansions = 0
        consecutive_contractions = 0
        consecutive_dry = 0
        
        if previous_events:
            sorted_prev = sorted(previous_events, key=lambda e: e.timestamp)
            
            # Count backwards from the last event to find consecutive sequences
            # Since multiple events can happen at the same timestamp (e.g. EXPANSION and CLIMAX),
            # we group events by timestamp
            grouped_by_ts: Dict[Any, List[VolumeEvent]] = {}
            for e in sorted_prev:
                grouped_by_ts.setdefault(e.timestamp, []).append(e)
                
            sorted_ts = sorted(grouped_by_ts.keys(), reverse=True)
            
            # We assume consecutive means "adjacent candles in the provided history"
            # But we don't have the full continuous candle history here, only the previous events.
            # To be 100% accurate, we would need to know if the events happened on adjacent *candles*.
            # For this implementation, we will track consecutive states during the current batch processing.
            # If we need absolute consecutive counts across batches, we might need a more robust state.
            # We will use the metadata of the very last event if it matches.
            
            # Check the most recent timestamp events
            if sorted_ts:
                recent_events = grouped_by_ts[sorted_ts[0]]
                for e in recent_events:
                    if e.event_type == VolumeEventType.EXPANSION:
                        consecutive_expansions = e.metadata.get("consecutive_count", 1) if e.metadata else 1
                    elif e.event_type == VolumeEventType.CONTRACTION:
                        consecutive_contractions = e.metadata.get("consecutive_count", 1) if e.metadata else 1
                    elif e.event_type == VolumeEventType.DRY_VOLUME:
                        consecutive_dry = e.metadata.get("consecutive_count", 1) if e.metadata else 1

        for i in range(len(analysis_results)):
            res = analysis_results[i]
            candle = candles[i]
            
            is_expansion = False
            is_contraction = False
            is_dry = False
            
            # 1. Evaluate current state using explicit threshold rules:
            # - EXPANSION: RVOL >= expansion_threshold
            # - CONTRACTION: RVOL <= contraction_threshold
            # - DRY VOLUME: RVOL <= dry_volume_threshold
            # - CLIMAX: RVOL >= climax_threshold
            if res.rvol >= config.expansion_threshold:
                is_expansion = True
                consecutive_expansions += 1
            else:
                consecutive_expansions = 0
                
            if res.rvol <= config.contraction_threshold:
                is_contraction = True
                consecutive_contractions += 1
            else:
                consecutive_contractions = 0
                
            if res.rvol <= config.dry_volume_threshold:
                is_dry = True
                consecutive_dry += 1
            else:
                consecutive_dry = 0
                
            # Classify the candle
            candle_cls = self._classify_candle(candle)
            
            # 2. Generate Events
            # CLIMAX
            if res.rvol >= config.climax_threshold:
                events.append(self._create_event(
                    candle=candle,
                    res=res,
                    event_type=VolumeEventType.CLIMAX,
                    candle_cls=candle_cls
                ))
            
            # EXPANSION
            if is_expansion:
                events.append(self._create_event(
                    candle=candle,
                    res=res,
                    event_type=VolumeEventType.EXPANSION,
                    candle_cls=candle_cls,
                    metadata={"consecutive_count": consecutive_expansions}
                ))
                
            # DRY VOLUME
            if is_dry:
                events.append(self._create_event(
                    candle=candle,
                    res=res,
                    event_type=VolumeEventType.DRY_VOLUME,
                    candle_cls=candle_cls,
                    metadata={"consecutive_count": consecutive_dry}
                ))
            # CONTRACTION (Emit both if needed)
            if is_contraction:
                events.append(self._create_event(
                    candle=candle,
                    res=res,
                    event_type=VolumeEventType.CONTRACTION,
                    candle_cls=candle_cls,
                    metadata={"consecutive_count": consecutive_contractions}
                ))
                
        return events

    def _classify_candle(self, candle: Candle) -> CandleClassification:
        o = float(candle.open)
        c = float(candle.close)
        if c > o:
            return CandleClassification.BULLISH
        elif c < o:
            return CandleClassification.BEARISH
        return CandleClassification.NEUTRAL

    def _create_event(self, candle: Candle, res: VolumeAnalysisResult, event_type: VolumeEventType, candle_cls: CandleClassification, metadata: dict = None) -> VolumeEvent:
        return VolumeEvent(
            event_id=str(uuid.uuid4()),
            symbol_id=res.symbol.symbol, # Simple mapping
            symbol=res.symbol,
            timeframe=res.timeframe,
            dataset_version=res.dataset_version,
            timestamp=res.timestamp,
            event_type=event_type,
            event_strength=res.rvol,
            relative_volume=res.rvol,
            candle_classification=candle_cls,
            trigger_candle=candle,
            metadata=metadata or {}
        )
