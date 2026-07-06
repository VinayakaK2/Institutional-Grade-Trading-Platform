from typing import List
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.models.zone import Zone, ZoneType
from backend.support_resistance_engine.contracts.engine import ZoneLifecycleContract

class ZoneLifecycleManager(ZoneLifecycleContract):
    def update_zones(self, active_zones: List[Zone], new_candles: List[Candle]) -> List[Zone]:
        for zone in active_zones:
            if not zone.is_active:
                continue
                
            for candle in new_candles:
                # If candle is from the past relative to the source swing, skip it for touches
                # We only evaluate candles that happen after the swing point.
                if candle.timestamp <= zone.source_swing_point.timestamp:
                    continue
                
                # Zone Age
                zone.strength.zone_age_candles += 1
                
                candle_high = float(candle.high)
                candle_low = float(candle.low)
                candle_close = float(candle.close)
                
                if zone.zone_type == ZoneType.SUPPORT:
                    # Touches upper boundary of support
                    touched = candle_low <= zone.upper_boundary
                    invalidated = candle_close < zone.lower_boundary
                    
                    if touched:
                        zone.strength.touch_count += 1
                        zone.strength.last_interaction_timestamp = candle.timestamp
                        
                        if invalidated:
                            zone.is_active = False
                            break  # Zone is dead, stop processing further candles for it
                        else:
                            zone.strength.rejection_count += 1
                            
                elif zone.zone_type == ZoneType.RESISTANCE:
                    # Touches lower boundary of resistance
                    touched = candle_high >= zone.lower_boundary
                    invalidated = candle_close > zone.upper_boundary
                    
                    if touched:
                        zone.strength.touch_count += 1
                        zone.strength.last_interaction_timestamp = candle.timestamp
                        
                        if invalidated:
                            zone.is_active = False
                            break
                        else:
                            zone.strength.rejection_count += 1
                            
        return active_zones

    def merge_zones(self, zones: List[Zone]) -> List[Zone]:
        """
        Merges overlapping active zones of the same type.
        Creates a wider zone combining the boundaries and summing the strength.
        """
        active = [z for z in zones if z.is_active]
        inactive = [z for z in zones if not z.is_active]
        
        if not active:
            return inactive
            
        # Separate by type
        supports = [z for z in active if z.zone_type == ZoneType.SUPPORT]
        resistances = [z for z in active if z.zone_type == ZoneType.RESISTANCE]
        
        merged_supports = self._merge_list(supports)
        merged_resistances = self._merge_list(resistances)
        
        return inactive + merged_supports + merged_resistances
        
    def _merge_list(self, zones: List[Zone]) -> List[Zone]:
        if not zones:
            return []
            
        # Sort by lower boundary to easily find overlaps
        sorted_zones = sorted(zones, key=lambda z: z.lower_boundary)
        merged = []
        
        current = sorted_zones[0]
        for next_zone in sorted_zones[1:]:
            # Check overlap
            if next_zone.lower_boundary <= current.upper_boundary:
                # Merge current and next_zone
                new_upper = max(current.upper_boundary, next_zone.upper_boundary)
                new_lower = min(current.lower_boundary, next_zone.lower_boundary)
                new_center = (new_upper + new_lower) / 2.0
                
                current.upper_boundary = new_upper
                current.lower_boundary = new_lower
                current.center = new_center
                
                # Combine strength heuristically
                current.strength.touch_count += next_zone.strength.touch_count
                current.strength.rejection_count += next_zone.strength.rejection_count
                
                if next_zone.strength.last_interaction_timestamp:
                    if not current.strength.last_interaction_timestamp or next_zone.strength.last_interaction_timestamp > current.strength.last_interaction_timestamp:
                        current.strength.last_interaction_timestamp = next_zone.strength.last_interaction_timestamp
                
                current.strength.zone_age_candles = max(current.strength.zone_age_candles, next_zone.strength.zone_age_candles)
            else:
                merged.append(current)
                current = next_zone
                
        merged.append(current)
        return merged
