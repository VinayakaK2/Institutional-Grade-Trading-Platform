from typing import List, Tuple
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.contracts.engine import VolumeAnalysisEngineContract
from backend.volume_analysis_engine.contracts.analyzer import RelativeVolumeAnalyzerContract, VolumeClassifierContract, VolumeEventDetectorContract
from backend.volume_analysis_engine.contracts.repository import VolumeAnalysisRepositoryContract
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig, AverageVolumeType
from backend.indicator_engine.calculators.sma import VolumeSMACalculator
from backend.indicator_engine.calculators.ema import VolumeEMACalculator

class VolumeAnalysisEngine(VolumeAnalysisEngineContract):
    def __init__(
        self,
        rvol_analyzer: RelativeVolumeAnalyzerContract,
        volume_classifier: VolumeClassifierContract,
        event_detector: VolumeEventDetectorContract,
        repository: VolumeAnalysisRepositoryContract
    ):
        self.rvol_analyzer = rvol_analyzer
        self.volume_classifier = volume_classifier
        self.event_detector = event_detector
        self.repository = repository

    def process_candles(self, candles: List[Candle], dataset_version: str, config: VolumeAnalysisConfig) -> Tuple[List[VolumeAnalysisResult], List[VolumeEvent]]:
        if not candles:
            return [], []
            
        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        
        # 1. Average Volume Calculator
        if config.avg_volume_type == AverageVolumeType.SMA:
            calc = VolumeSMACalculator()
        else:
            calc = VolumeEMACalculator()
            
        # Indicator Engine calculators return IndicatorResult starting from period-1.
        # We need to map them back to match the candle array.
        # To make it simple, we just extract the values.
        indicator_results = calc.calculate(candles, dataset_version, period=config.avg_volume_period)
        
        # Map values by timestamp to align with candles easily
        val_map = {res.timestamp: res.value for res in indicator_results}
        
        # We only process candles that have a computed average volume
        valid_candles = []
        avg_volumes = []
        for c in candles:
            if c.timestamp in val_map:
                valid_candles.append(c)
                avg_volumes.append(val_map[c.timestamp])
                
        if not valid_candles:
            return [], []
            
        if len(valid_candles) < config.minimum_history_required:
            raise ValueError(f"Insufficient history after average volume calc: {len(valid_candles)} < {config.minimum_history_required}")
            
        # Fetch previous state
        previous_events = self.repository.get_events(symbol, timeframe, dataset_version)
        
        # 2. Relative Volume Analyzer
        raw_results = self.rvol_analyzer.analyze(valid_candles, avg_volumes, dataset_version, config)
        
        # 3. Volume Classifier
        classified_results = self.volume_classifier.classify(raw_results, config)
        
        # 4. Volume Event Detector
        new_events = self.event_detector.detect_events(valid_candles, classified_results, config, previous_events)
        
        # 5. Repository
        self.repository.save_analysis(classified_results, new_events)
        
        return classified_results, new_events
