import uuid
from typing import List, Optional
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.market_structure_engine.contracts.analyzer import StructureAnalyzerContract
import logging

logger = logging.getLogger(__name__)

class StructureAnalyzer(StructureAnalyzerContract):
    def classify_swings(self, swings: List[SwingPoint], previous_structure: List[MarketStructurePoint]) -> List[MarketStructurePoint]:
        if not swings:
            return []
            
        # 1. Enforce chronological order
        swings = sorted(swings, key=lambda s: s.timestamp)
        
        # 2. Filter duplicate timestamps and enforce strict alternation
        filtered_swings = self._enforce_alternation(swings)
        
        # 3. Classify HH, HL, LH, LL
        classified_points = []
        
        last_high: Optional[MarketStructurePoint] = None
        last_low: Optional[MarketStructurePoint] = None
        
        # Populate initial state from previous structure
        for p in reversed(previous_structure):
            if p.type in (StructureType.HH, StructureType.LH) and last_high is None:
                last_high = p
            elif p.type in (StructureType.HL, StructureType.LL) and last_low is None:
                last_low = p
            if last_high and last_low:
                break
                
        for swing in filtered_swings:
            # Check for duplicate against previous_structure to avoid inserting same timestamp twice
            if previous_structure and swing.timestamp <= previous_structure[-1].swing_point.timestamp:
                logger.warning(f"Rejecting swing at {swing.timestamp}: older or equal to last previous structure.")
                continue

            point_id = str(uuid.uuid4())
            
            if swing.type == SwingType.HIGH:
                if last_high is None:
                    # Initial high is arbitrarily considered HH
                    s_type = StructureType.HH
                else:
                    if swing.price > last_high.swing_point.price:
                        s_type = StructureType.HH
                    else:
                        s_type = StructureType.LH
                        
                point = MarketStructurePoint(id=point_id, swing_point=swing, type=s_type)
                last_high = point
                classified_points.append(point)
                
            elif swing.type == SwingType.LOW:
                if last_low is None:
                    # Initial low is arbitrarily considered HL
                    s_type = StructureType.HL
                else:
                    if swing.price > last_low.swing_point.price:
                        s_type = StructureType.HL
                    else:
                        s_type = StructureType.LL
                        
                point = MarketStructurePoint(id=point_id, swing_point=swing, type=s_type)
                last_low = point
                classified_points.append(point)
                
        return classified_points

    def _enforce_alternation(self, swings: List[SwingPoint]) -> List[SwingPoint]:
        if not swings:
            return []
            
        # Remove identical timestamps first
        unique_swings = []
        seen_timestamps = set()
        for s in swings:
            if s.timestamp in seen_timestamps:
                raise ValueError(f"Duplicate swing timestamp detected: {s.timestamp}")
            seen_timestamps.add(s.timestamp)
            unique_swings.append(s)
            
        alternated = []
        current_type = None
        current_extreme = None
        
        for swing in unique_swings:
            if current_type is None:
                current_type = swing.type
                current_extreme = swing
                continue
                
            if swing.type == current_type:
                # Consecutive same-type swings. Keep the extreme one.
                if current_type == SwingType.HIGH:
                    if swing.price > current_extreme.price:
                        current_extreme = swing
                elif current_type == SwingType.LOW:
                    if swing.price < current_extreme.price:
                        current_extreme = swing
            else:
                # Type changed, we can push the current extreme and start new
                alternated.append(current_extreme)
                current_type = swing.type
                current_extreme = swing
                
        if current_extreme:
            alternated.append(current_extreme)
            
        return alternated
