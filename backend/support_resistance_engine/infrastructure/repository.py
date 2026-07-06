from typing import List, Optional
from datetime import datetime, timezone
import json

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.support_resistance_engine.models.zone import Zone, ZoneType, SwingPoint, ZoneStrength
from backend.support_resistance_engine.contracts.repository import (
    SupportResistanceRepositoryContract,
    SupportResistanceQueryContract
)
from backend.infrastructure.database.orm.support_resistance import SupportResistanceZoneModel
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class PostgreSQLSupportResistanceRepository(SupportResistanceRepositoryContract, SupportResistanceQueryContract):
    def __init__(self, db_session: Session):
        self.db = db_session

    def save_zones(self, zones: List[Zone]) -> None:
        if not zones:
            return
            
        for zone in zones:
            # Upsert logic depending on whether we use merge or not. We'll use merge.
            model = SupportResistanceZoneModel(
                id=zone.id,
                symbol=zone.symbol.symbol,
                timeframe=zone.timeframe.value,
                dataset_version=zone.dataset_version,
                zone_type=zone.zone_type.value,
                center=zone.center,
                upper_boundary=zone.upper_boundary,
                lower_boundary=zone.lower_boundary,
                created_at=zone.created_at,
                source_swing_point=json.loads(zone.source_swing_point.model_dump_json()),
                symbol_reference=json.loads(zone.symbol.model_dump_json()),
                strength=json.loads(zone.strength.model_dump_json()),
                is_active=zone.is_active
            )
            self.db.merge(model)
        self.db.commit()

    def update_zones(self, zones: List[Zone]) -> None:
        self.save_zones(zones)

    def _model_to_zone(self, model: SupportResistanceZoneModel) -> Zone:
        swing_point = SwingPoint(**model.source_swing_point)
        strength = ZoneStrength(**model.strength)
        symbol_ref = SymbolReference(**model.symbol_reference)
        
        # In Python < 3.11, some datetime fields from JSON might be strings, Pydantic handles parsing
        # but created_at is from DB, so we ensure tzinfo.
        created = model.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
            
        return Zone(
            id=model.id,
            symbol=symbol_ref,
            timeframe=Timeframe(model.timeframe),
            dataset_version=model.dataset_version,
            zone_type=ZoneType(model.zone_type),
            center=model.center,
            upper_boundary=model.upper_boundary,
            lower_boundary=model.lower_boundary,
            created_at=created,
            source_swing_point=swing_point,
            strength=strength,
            is_active=model.is_active
        )

    def get_active_zones(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> List[Zone]:
        stmt = select(SupportResistanceZoneModel).where(
            SupportResistanceZoneModel.symbol == symbol.symbol,
            SupportResistanceZoneModel.timeframe == timeframe.value,
            SupportResistanceZoneModel.dataset_version == dataset_version,
            SupportResistanceZoneModel.is_active
        ).order_by(SupportResistanceZoneModel.created_at.desc())
        results = self.db.execute(stmt).scalars().all()
        return [self._model_to_zone(r) for r in results]

    def get_historical_zones(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Zone]:
        stmt = select(SupportResistanceZoneModel).where(
            SupportResistanceZoneModel.symbol == symbol.symbol,
            SupportResistanceZoneModel.timeframe == timeframe.value,
            SupportResistanceZoneModel.dataset_version == dataset_version
        )
        if start_time:
            stmt = stmt.where(SupportResistanceZoneModel.created_at >= start_time)
        if end_time:
            stmt = stmt.where(SupportResistanceZoneModel.created_at <= end_time)
            
        stmt = stmt.order_by(SupportResistanceZoneModel.created_at.asc())
        results = self.db.execute(stmt).scalars().all()
        return [self._model_to_zone(r) for r in results]

    def get_nearest_zones(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        current_price: float, 
        limit: int = 1
    ) -> List[Zone]:
        active_zones = self.get_active_zones(symbol, timeframe, dataset_version)
        
        # Sort by distance to current_price
        sorted_zones = sorted(active_zones, key=lambda z: abs(z.center - current_price))
        return sorted_zones[:limit]
