import uuid
from typing import List
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, RVOLClassification
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig
from backend.volume_analysis_engine.contracts.analyzer import RelativeVolumeAnalyzerContract, VolumeClassifierContract
import logging

logger = logging.getLogger(__name__)

class RelativeVolumeAnalyzer(RelativeVolumeAnalyzerContract):
    def analyze(self, candles: List[Candle], avg_volumes: List[float], dataset_version: str, config: VolumeAnalysisConfig) -> List[VolumeAnalysisResult]:
        """
        Computes RVOL and initializes VolumeAnalysisResult with NORMAL classification.
        """
        if not candles or not avg_volumes:
            return []
            
        if len(candles) != len(avg_volumes):
            raise ValueError(f"Candles ({len(candles)}) and Average Volumes ({len(avg_volumes)}) length mismatch")
            
        if len(candles) < config.minimum_history_required:
            raise ValueError(f"Insufficient history: {len(candles)} < {config.minimum_history_required}")
            
        results = []
        for i in range(len(candles)):
            candle = candles[i]
            vol = float(candle.volume)
            avg_vol = avg_volumes[i]
            
            # Avoid division by zero
            rvol = (vol / avg_vol) if avg_vol > 0 else 0.0
            
            results.append(VolumeAnalysisResult(
                id=str(uuid.uuid4()),
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                volume=vol,
                avg_volume=avg_vol,
                rvol=rvol,
                classification=RVOLClassification.NORMAL
            ))
            
        return results

class VolumeClassifier(VolumeClassifierContract):
    def classify(self, results: List[VolumeAnalysisResult], config: VolumeAnalysisConfig) -> List[VolumeAnalysisResult]:
        """
        Classifies RVOL as NORMAL, HIGH, LOW based on configuration thresholds.
        
        Rules:
        - HIGH: RVOL is greater than or equal (>=) to expansion_threshold.
        - LOW: RVOL is less than or equal (<=) to contraction_threshold.
        - NORMAL: RVOL is between contraction_threshold and expansion_threshold.
        """
        classified = []
        for res in results:
            cls = RVOLClassification.NORMAL
            if res.rvol >= config.expansion_threshold:
                cls = RVOLClassification.HIGH
            elif res.rvol <= config.contraction_threshold:
                cls = RVOLClassification.LOW
                
            classified.append(
                VolumeAnalysisResult(
                    id=res.id,
                    symbol=res.symbol,
                    timeframe=res.timeframe,
                    dataset_version=res.dataset_version,
                    timestamp=res.timestamp,
                    volume=res.volume,
                    avg_volume=res.avg_volume,
                    rvol=res.rvol,
                    classification=cls
                )
            )
        return classified
