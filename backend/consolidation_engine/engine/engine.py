from typing import List

from backend.market_data.models.candle import Candle
from backend.consolidation_engine.models.models import ConsolidationCandidate, ConsolidationSnapshot
from backend.consolidation_engine.models.fingerprint import BusinessFingerprint
from backend.consolidation_engine.contracts.contracts import (
    IBoundaryDetectionStrategy,
    ICandleContainmentStrategy,
    IWindowRequirement
)
from backend.consolidation_engine.detection.range import RangeDetector
from backend.consolidation_engine.detection.inclusion import CandleInclusionValidator

class ConsolidationDetectionEngine:
    """
    Stateless orchestrator for Consolidation Detection.
    Orchestrates boundary detection and candle inclusion.
    Does not own any business logic heuristics.
    """
    
    def __init__(
        self,
        window_requirement: IWindowRequirement,
        boundary_strategy: IBoundaryDetectionStrategy,
        containment_strategy: ICandleContainmentStrategy
    ):
        self._window_requirement = window_requirement
        self._boundary_strategy = boundary_strategy
        self._range_detector = RangeDetector(boundary_strategy)
        self._inclusion_validator = CandleInclusionValidator(containment_strategy)
        
    def detect(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        fingerprint: BusinessFingerprint,
        snapshot_version: int,
        config_version: int
    ) -> ConsolidationSnapshot:
        """
        Orchestrates consolidation detection using injected strategies.
        Returns a deterministic immutable snapshot.
        """
        min_candles = self._window_requirement.get_minimum_candles()
        candidates = []
        
        if not candles or len(candles) < min_candles:
            return self._build_snapshot(fingerprint, snapshot_version, config_version, [])
            
        i = 0
        while i <= len(candles) - min_candles:
            window = candles[i:i + min_candles]
            
            upper, lower, mid = self._range_detector.detect_range(window)
            
            base_contained = all(
                self._inclusion_validator.validate_inclusion(c, upper, lower)
                for c in window
            )
            
            if base_contained:
                end_idx = i + min_candles - 1
                while end_idx + 1 < len(candles):
                    next_candle = candles[end_idx + 1]
                    if self._inclusion_validator.validate_inclusion(next_candle, upper, lower):
                        end_idx += 1
                    else:
                        break
                        
                cons_candles = candles[i:end_idx + 1]
                start_time = cons_candles[0].timestamp
                end_time = cons_candles[-1].timestamp
                duration_sec = int((end_time - start_time).total_seconds())
                
                candidate_id = ConsolidationCandidate.generate_id(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_timestamp=start_time,
                    end_timestamp=end_time,
                    business_fingerprint=fingerprint.compute_hash()
                )
                
                candidate = ConsolidationCandidate(
                    candidate_id=candidate_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_timestamp=start_time,
                    end_timestamp=end_time,
                    upper_boundary=upper,
                    lower_boundary=lower,
                    midpoint=mid,
                    duration=duration_sec,
                    candle_count=len(cons_candles)
                )
                candidates.append(candidate)
                
                i = end_idx + 1
            else:
                i += 1
                
        return self._build_snapshot(fingerprint, snapshot_version, config_version, candidates)

    def _build_snapshot(
        self,
        fingerprint: BusinessFingerprint,
        snapshot_version: int,
        config_version: int,
        candidates: List[ConsolidationCandidate]
    ) -> ConsolidationSnapshot:
        return ConsolidationSnapshot(
            snapshot_version=snapshot_version,
            parent_dataset_version=fingerprint.parent_dataset_version,
            parent_trend_snapshot_version=fingerprint.parent_trend_snapshot_version,
            pipeline_version=fingerprint.pipeline_version,
            engine_version=fingerprint.engine_version,
            config_version=config_version,
            config_hash=fingerprint.config_hash,
            business_fingerprint=fingerprint.compute_hash(),
            fingerprint_algorithm_version=fingerprint.fingerprint_algorithm_version,
            candidates=candidates
        )
