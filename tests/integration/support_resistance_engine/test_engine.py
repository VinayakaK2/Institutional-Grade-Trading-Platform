import pytest
from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.database.orm.base import Base
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe

from backend.support_resistance_engine.engine.swing import SwingDetector
from backend.support_resistance_engine.engine.zone_generator import ZoneGenerator
from backend.support_resistance_engine.engine.lifecycle import ZoneLifecycleManager
from backend.support_resistance_engine.infrastructure.repository import PostgreSQLSupportResistanceRepository
from backend.support_resistance_engine.engine.engine import SupportResistanceEngine

@pytest.fixture
def db_session():
    # Use in-memory SQLite for testing repository
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_candles() -> List[Candle]:
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    candles = []
    
    for i in range(20):
        # Default flat
        c_high = 10.0
        c_low = 5.0
        
        if i == 5:
            c_high = 20.0
        elif i == 15:
            c_low = 1.0
            
        candles.append(Candle(
            symbol=sym,
            timeframe=tf,
            timestamp=base_time + timedelta(days=i),
            open=7.0,
            high=c_high,
            low=c_low,
            close=8.0,
            volume=100.0,
            is_completed=True
        ))
    return candles

def test_engine_integration(db_session, sample_candles):
    detector = SwingDetector(lookback=3, lookforward=3)
    generator = ZoneGenerator()
    lifecycle = ZoneLifecycleManager()
    repo = PostgreSQLSupportResistanceRepository(db_session)
    
    engine = SupportResistanceEngine(
        swing_detector=detector,
        zone_generator=generator,
        lifecycle_manager=lifecycle,
        repository=repo
    )
    
    zones = engine.process_candles(sample_candles, "CANONICAL")
    
    assert len(zones) >= 2
    
    # Check Repo
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    active_zones = repo.get_active_zones(sym, tf, "CANONICAL")
    assert len(active_zones) == len([z for z in zones if z.is_active])
    
    nearest = repo.get_nearest_zones(sym, tf, "CANONICAL", current_price=10.0, limit=2)
    assert len(nearest) == 2
