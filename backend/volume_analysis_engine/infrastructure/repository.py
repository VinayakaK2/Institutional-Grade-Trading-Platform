import json
from typing import List, Optional
from datetime import timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.contracts.repository import VolumeAnalysisRepositoryContract
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent, VolumeEventType, RVOLClassification, CandleClassification
from backend.infrastructure.database.orm.volume_analysis import VolumeAnalysisModel, VolumeEventModel

class PostgreSQLVolumeRepository(VolumeAnalysisRepositoryContract):
    def __init__(self, db_session: Session):
        self.db = db_session

    def save_analysis(self, results: List[VolumeAnalysisResult], events: List[VolumeEvent]) -> None:
        if results:
            for r in results:
                model = VolumeAnalysisModel(
                    id=r.id,
                    symbol=r.symbol.symbol,
                    timeframe=r.timeframe.value,
                    dataset_version=r.dataset_version,
                    timestamp=r.timestamp,
                    volume=r.volume,
                    avg_volume=r.avg_volume,
                    rvol=r.rvol,
                    classification=r.classification.value,
                    symbol_reference=json.loads(r.symbol.model_dump_json())
                )
                self.db.merge(model)
                
        if events:
            for e in events:
                model = VolumeEventModel(
                    id=e.event_id,
                    symbol_id=e.symbol_id,
                    symbol=e.symbol.symbol,
                    timeframe=e.timeframe.value,
                    dataset_version=e.dataset_version,
                    timestamp=e.timestamp,
                    event_type=e.event_type.value,
                    event_strength=e.event_strength,
                    relative_volume=e.relative_volume,
                    candle_classification=e.candle_classification.value,
                    trigger_candle=json.loads(e.trigger_candle.model_dump_json()),
                    symbol_reference=json.loads(e.symbol.model_dump_json()),
                    metadata_json=e.metadata
                )
                self.db.merge(model)
                
        if results or events:
            self.db.commit()

    def get_analysis_results(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[VolumeAnalysisResult]:
        stmt = select(VolumeAnalysisModel).where(
            VolumeAnalysisModel.symbol == symbol.symbol,
            VolumeAnalysisModel.timeframe == timeframe.value,
            VolumeAnalysisModel.dataset_version == dataset_version
        ).order_by(VolumeAnalysisModel.timestamp.asc())
        
        if limit is not None:
            stmt = stmt.limit(limit)
            
        db_res = self.db.execute(stmt).scalars().all()
        return [self._map_res_to_domain(r) for r in db_res]

    def get_events(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[VolumeEvent]:
        stmt = select(VolumeEventModel).where(
            VolumeEventModel.symbol == symbol.symbol,
            VolumeEventModel.timeframe == timeframe.value,
            VolumeEventModel.dataset_version == dataset_version
        ).order_by(VolumeEventModel.timestamp.asc())
        
        if limit is not None:
            stmt = stmt.limit(limit)
            
        db_ev = self.db.execute(stmt).scalars().all()
        return [self._map_event_to_domain(e) for e in db_ev]

    def _map_res_to_domain(self, m: VolumeAnalysisModel) -> VolumeAnalysisResult:
        sym = SymbolReference(**m.symbol_reference)
        ts = m.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
            
        return VolumeAnalysisResult(
            id=m.id,
            symbol=sym,
            timeframe=Timeframe(m.timeframe),
            dataset_version=m.dataset_version,
            timestamp=ts,
            volume=m.volume,
            avg_volume=m.avg_volume,
            rvol=m.rvol,
            classification=RVOLClassification(m.classification)
        )

    def _map_event_to_domain(self, m: VolumeEventModel) -> VolumeEvent:
        sym = SymbolReference(**m.symbol_reference)
        candle = Candle(**m.trigger_candle)
        ts = m.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
            
        return VolumeEvent(
            event_id=m.id,
            symbol_id=m.symbol_id,
            symbol=sym,
            timeframe=Timeframe(m.timeframe),
            dataset_version=m.dataset_version,
            timestamp=ts,
            event_type=VolumeEventType(m.event_type),
            event_strength=m.event_strength,
            relative_volume=m.relative_volume,
            candle_classification=CandleClassification(m.candle_classification),
            trigger_candle=candle,
            metadata=m.metadata_json or {}
        )
