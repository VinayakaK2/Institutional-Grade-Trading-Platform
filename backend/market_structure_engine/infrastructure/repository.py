import json
from typing import List, Optional
from datetime import timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.market_structure_engine.contracts.repository import MarketStructureRepositoryContract
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.market_structure_engine.models.events import StructureEvent, EventType, EventSignal
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.support_resistance_engine.models.zone import SwingPoint
from backend.market_data.models.candle import Candle
from backend.infrastructure.database.orm.market_structure import MarketStructurePointModel, MarketStructureEventModel

class PostgreSQLMarketStructureRepository(MarketStructureRepositoryContract):
    def __init__(self, db_session: Session):
        self.db = db_session

    def save_structure_points(self, points: List[MarketStructurePoint], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> None:
        if not points:
            return
            
        for p in points:
            model = MarketStructurePointModel(
                id=p.id,
                symbol=symbol.symbol,
                timeframe=timeframe.value,
                dataset_version=dataset_version,
                structure_type=p.type.value,
                timestamp=p.swing_point.timestamp,
                swing_point=json.loads(p.swing_point.model_dump_json()),
                symbol_reference=json.loads(symbol.model_dump_json())
            )
            self.db.merge(model)
        self.db.commit()

    def save_structure_events(self, events: List[StructureEvent], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> None:
        if not events:
            return
            
        for e in events:
            model = MarketStructureEventModel(
                id=e.id,
                symbol=symbol.symbol,
                timeframe=timeframe.value,
                dataset_version=dataset_version,
                event_type=e.type.value,
                event_signal=e.signal.value,
                timestamp=e.timestamp,
                trigger_candle=json.loads(e.trigger_candle.model_dump_json()),
                reference_swing=json.loads(e.reference_swing.model_dump_json()),
                symbol_reference=json.loads(symbol.model_dump_json())
            )
            self.db.merge(model)
        self.db.commit()

    def get_structure_points(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[MarketStructurePoint]:
        stmt = select(MarketStructurePointModel).where(
            MarketStructurePointModel.symbol == symbol.symbol,
            MarketStructurePointModel.timeframe == timeframe.value,
            MarketStructurePointModel.dataset_version == dataset_version
        ).order_by(MarketStructurePointModel.timestamp.asc())
        
        if limit is not None:
            stmt = stmt.limit(limit)
            
        results = self.db.execute(stmt).scalars().all()
        return [self._point_model_to_domain(r) for r in results]

    def get_structure_events(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[StructureEvent]:
        stmt = select(MarketStructureEventModel).where(
            MarketStructureEventModel.symbol == symbol.symbol,
            MarketStructureEventModel.timeframe == timeframe.value,
            MarketStructureEventModel.dataset_version == dataset_version
        ).order_by(MarketStructureEventModel.timestamp.asc())
        
        if limit is not None:
            stmt = stmt.limit(limit)
            
        results = self.db.execute(stmt).scalars().all()
        return [self._event_model_to_domain(r) for r in results]

    def _point_model_to_domain(self, model: MarketStructurePointModel) -> MarketStructurePoint:
        swing = SwingPoint(**model.swing_point)
        # Fix tz if missing
        if swing.timestamp.tzinfo is None:
            swing = SwingPoint(**{**model.swing_point, "timestamp": swing.timestamp.replace(tzinfo=timezone.utc)})
            
        return MarketStructurePoint(
            id=model.id,
            swing_point=swing,
            type=StructureType(model.structure_type)
        )

    def _event_model_to_domain(self, model: MarketStructureEventModel) -> StructureEvent:
        candle = Candle(**model.trigger_candle)
        swing = SwingPoint(**model.reference_swing)
        
        ts = model.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
            
        return StructureEvent(
            id=model.id,
            type=EventType(model.event_type),
            signal=EventSignal(model.event_signal),
            trigger_candle=candle,
            reference_swing=swing,
            timestamp=ts
        )
