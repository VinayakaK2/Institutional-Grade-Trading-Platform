from typing import List
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.models.zone import Zone
from backend.support_resistance_engine.contracts.engine import (
    SwingDetectorContract,
    ZoneGeneratorContract,
    ZoneLifecycleContract,
    SupportResistanceEngineContract
)
from backend.support_resistance_engine.contracts.repository import SupportResistanceRepositoryContract

class SupportResistanceEngine(SupportResistanceEngineContract):
    def __init__(
        self,
        swing_detector: SwingDetectorContract,
        zone_generator: ZoneGeneratorContract,
        lifecycle_manager: ZoneLifecycleContract,
        repository: SupportResistanceRepositoryContract
    ):
        self.swing_detector = swing_detector
        self.zone_generator = zone_generator
        self.lifecycle_manager = lifecycle_manager
        self.repository = repository

    def process_candles(self, candles: List[Candle], dataset_version: str) -> List[Zone]:
        if not candles:
            return []
        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        
        # 1. Detect Swings
        swings = self.swing_detector.detect_swings(candles)
        
        # 2. Generate new Zones
        new_zones = self.zone_generator.generate_zones(swings, symbol, timeframe, dataset_version)
        
        # 3. We need to update existing zones if we were doing this incrementally,
        # but process_candles usually processes a batch and generates everything from scratch,
        # or updates from previous state. 
        # For simplicity in this core architecture, we'll treat process_candles as:
        # Load active zones for this dataset, update them with ALL candles, then merge, then save.
        # Actually, since it's a batch process over all candles, we can just run the lifecycle
        # over the newly generated zones using the candles that came AFTER the zone was created.
        
        # Run lifecycle on the generated zones using the whole candle series.
        # The lifecycle manager ignores candles prior to the zone's source swing.
        updated_zones = self.lifecycle_manager.update_zones(new_zones, candles)
        
        # 4. Merge overlapping zones
        merged_zones = self.lifecycle_manager.merge_zones(updated_zones)
        
        # 5. Persist
        self.repository.save_zones(merged_zones)
        
        return merged_zones
