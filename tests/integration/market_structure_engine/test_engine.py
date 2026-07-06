import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.database.orm.base import Base
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle

from backend.support_resistance_engine.engine.swing import SwingDetector
from backend.market_structure_engine.engine.analyzer import StructureAnalyzer
from backend.market_structure_engine.engine.event_detector import EventDetector
from backend.market_structure_engine.infrastructure.repository import PostgreSQLMarketStructureRepository
from backend.market_structure_engine.engine.engine import MarketStructureEngine
from backend.market_structure_engine.models.config import StructureConfig, ConfirmationRule

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_candles():
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    # We create a sequence of candles that form an HH -> HL -> HH sequence, and then a BoS
    candles = []
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    
    # High at 20.0
    for i in range(11):
        dt = base_time + timedelta(days=i)
        price = 10.0 + i if i <= 5 else 20.0 - (i - 5)
        candles.append(Candle(symbol=sym, timeframe=tf, timestamp=dt, open=price, high=price, low=price, close=price, volume=100, is_completed=True))
        
    # Low at 15.0
    for i in range(11, 21):
        dt = base_time + timedelta(days=i)
        price = 15.0 - (i - 11) if i <= 15 else 11.0 + (i - 15)
        candles.append(Candle(symbol=sym, timeframe=tf, timestamp=dt, open=price, high=price, low=price, close=price, volume=100, is_completed=True))
        
    # Candle that breaks 20.0 (BoS)
    candles.append(Candle(
        symbol=sym, timeframe=tf, timestamp=base_time + timedelta(days=25),
        open=21.0, high=22.0, low=20.5, close=21.5, volume=100, is_completed=True
    ))
    
    return candles

def test_market_structure_engine_integration(db_session, sample_candles):
    detector = SwingDetector(lookback=3, lookforward=3)
    analyzer = StructureAnalyzer()
    event_detector = EventDetector()
    repo = PostgreSQLMarketStructureRepository(db_session)
    
    engine = MarketStructureEngine(
        swing_detector=detector,
        structure_analyzer=analyzer,
        event_detector=event_detector,
        repository=repo
    )
    
    config = StructureConfig(confirmation_rule=ConfirmationRule.WICK_BREAK)
    
    points, events = engine.process_candles(sample_candles, "CANONICAL", config)
    
    assert len(points) >= 2 # Should find at least the HH and HL
    assert len(events) >= 1 # Should find the BoS
    
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    db_points = repo.get_structure_points(sym, tf, "CANONICAL")
    db_events = repo.get_structure_events(sym, tf, "CANONICAL")
    
    assert len(db_points) == len(points)
    assert len(db_events) == len(events)
