import uuid
from typing import List
from datetime import datetime, timezone
from backend.support_resistance_engine.models.zone import (
    SwingPoint, Zone, ZoneType, ZoneStrength, SwingType
)
from backend.support_resistance_engine.contracts.engine import ZoneGeneratorContract
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class ZoneGenerator(ZoneGeneratorContract):
    def generate_zones(self, swings: List[SwingPoint], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> List[Zone]:
        zones = []
        
        for swing in swings:
            zone_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            if swing.type == SwingType.LOW:
                # Support Zone: Lower = Swing Low, Upper = Body Low
                lower = swing.candle_low
                upper = min(swing.candle_open, swing.candle_close)
                # Ensure upper >= lower
                if upper < lower:
                    upper = lower
                    
                center = (upper + lower) / 2.0
                
                zone = Zone(
                    id=zone_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    dataset_version=dataset_version,
                    zone_type=ZoneType.SUPPORT,
                    center=center,
                    upper_boundary=upper,
                    lower_boundary=lower,
                    created_at=now,
                    source_swing_point=swing,
                    strength=ZoneStrength(),
                    is_active=True
                )
                zones.append(zone)
            else:
                # Resistance Zone: Upper = Swing High, Lower = Body High
                upper = swing.candle_high
                lower = max(swing.candle_open, swing.candle_close)
                # Ensure upper >= lower
                if lower > upper:
                    lower = upper
                    
                center = (upper + lower) / 2.0
                
                zone = Zone(
                    id=zone_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    dataset_version=dataset_version,
                    zone_type=ZoneType.RESISTANCE,
                    center=center,
                    upper_boundary=upper,
                    lower_boundary=lower,
                    created_at=now,
                    source_swing_point=swing,
                    strength=ZoneStrength(),
                    is_active=True
                )
                zones.append(zone)
                
        return zones
