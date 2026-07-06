from typing import List, Tuple
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.contracts.engine import SwingDetectorContract
from backend.market_structure_engine.contracts.engine import MarketStructureEngineContract
from backend.market_structure_engine.contracts.analyzer import StructureAnalyzerContract, EventDetectorContract
from backend.market_structure_engine.contracts.repository import MarketStructureRepositoryContract
from backend.market_structure_engine.models.structure import MarketStructurePoint
from backend.market_structure_engine.models.events import StructureEvent
from backend.market_structure_engine.models.config import StructureConfig

class MarketStructureEngine(MarketStructureEngineContract):
    def __init__(
        self,
        swing_detector: SwingDetectorContract,
        structure_analyzer: StructureAnalyzerContract,
        event_detector: EventDetectorContract,
        repository: MarketStructureRepositoryContract
    ):
        self.swing_detector = swing_detector
        self.structure_analyzer = structure_analyzer
        self.event_detector = event_detector
        self.repository = repository

    def process_candles(self, candles: List[Candle], dataset_version: str, config: StructureConfig) -> Tuple[List[MarketStructurePoint], List[StructureEvent]]:
        if not candles:
            return [], []
            
        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        
        # 1. Fetch previous state from repository (if incrementally processing)
        # For this batch processing implementation, we assume processing from scratch
        # or we could load all existing to append. We'll load existing to ensure continuity.
        previous_points = self.repository.get_structure_points(symbol, timeframe, dataset_version)
        previous_events = self.repository.get_structure_events(symbol, timeframe, dataset_version)
        
        # 2. Detect Swings (from raw candles)
        # The swing detector doesn't know about previous swings, it just detects them in the provided candles.
        swings = self.swing_detector.detect_swings(candles)
        
        # 3. Classify Swings into Structure Points
        new_points = self.structure_analyzer.classify_swings(swings, previous_points)
        
        # We need the full structural history for accurate event detection
        all_points = previous_points + new_points
        
        # 4. Detect BoS and ChoCH Events
        new_events = self.event_detector.detect_events(all_points, candles, config, previous_events)
        
        # 5. Persist
        self.repository.save_structure_points(new_points, symbol, timeframe, dataset_version)
        self.repository.save_structure_events(new_events, symbol, timeframe, dataset_version)
        
        return new_points, new_events
