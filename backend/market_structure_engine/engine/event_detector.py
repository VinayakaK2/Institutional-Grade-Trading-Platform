import uuid
from typing import List, Optional
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.market_structure_engine.models.events import StructureEvent, EventType, EventSignal
from backend.market_structure_engine.models.config import StructureConfig, ConfirmationRule
from backend.market_data.models.candle import Candle
from backend.market_structure_engine.contracts.analyzer import EventDetectorContract
import logging

logger = logging.getLogger(__name__)

class EventDetector(EventDetectorContract):
    def detect_events(
        self, 
        structure_points: List[MarketStructurePoint], 
        candles: List[Candle], 
        config: StructureConfig,
        previous_events: List[StructureEvent]
    ) -> List[StructureEvent]:
        
        events: List[StructureEvent] = []
        if not structure_points or not candles:
            return events
            
        # Sort everything chronologically
        points = sorted(structure_points, key=lambda p: p.swing_point.timestamp)
        candles = sorted(candles, key=lambda c: c.timestamp)
        
        # Track previously broken points to avoid duplicates
        broken_point_ids = set([e.reference_swing.timestamp for e in previous_events])
        
        # State tracking
        current_point_idx = 0
        latest_high: Optional[MarketStructurePoint] = None
        latest_low: Optional[MarketStructurePoint] = None
        
        for candle in candles:
            # Advance structure points up to the current candle
            while current_point_idx < len(points) and points[current_point_idx].swing_point.timestamp < candle.timestamp:
                p = points[current_point_idx]
                if p.type in (StructureType.HH, StructureType.LH):
                    latest_high = p
                elif p.type in (StructureType.HL, StructureType.LL):
                    latest_low = p
                current_point_idx += 1
                
            # Check for bullish break (break above latest_high)
            if latest_high and latest_high.swing_point.timestamp not in broken_point_ids:
                is_break = False
                if config.confirmation_rule == ConfirmationRule.WICK_BREAK:
                    if float(candle.high) > latest_high.swing_point.price:
                        is_break = True
                elif config.confirmation_rule == ConfirmationRule.BODY_CLOSE:
                    if float(candle.close) > latest_high.swing_point.price:
                        is_break = True
                        
                if is_break:
                    event_type = EventType.BOS if latest_high.type == StructureType.HH else EventType.CHOCH
                    events.append(
                        StructureEvent(
                            id=str(uuid.uuid4()),
                            type=event_type,
                            signal=EventSignal.BULLISH,
                            trigger_candle=candle,
                            reference_swing=latest_high.swing_point,
                            timestamp=candle.timestamp
                        )
                    )
                    broken_point_ids.add(latest_high.swing_point.timestamp)
            
            # Check for bearish break (break below latest_low)
            if latest_low and latest_low.swing_point.timestamp not in broken_point_ids:
                is_break = False
                if config.confirmation_rule == ConfirmationRule.WICK_BREAK:
                    if float(candle.low) < latest_low.swing_point.price:
                        is_break = True
                elif config.confirmation_rule == ConfirmationRule.BODY_CLOSE:
                    if float(candle.close) < latest_low.swing_point.price:
                        is_break = True
                        
                if is_break:
                    event_type = EventType.BOS if latest_low.type == StructureType.LL else EventType.CHOCH
                    events.append(
                        StructureEvent(
                            id=str(uuid.uuid4()),
                            type=event_type,
                            signal=EventSignal.BEARISH,
                            trigger_candle=candle,
                            reference_swing=latest_low.swing_point,
                            timestamp=candle.timestamp
                        )
                    )
                    broken_point_ids.add(latest_low.swing_point.timestamp)
                    
        return events
