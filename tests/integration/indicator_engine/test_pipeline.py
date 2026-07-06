import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.candle_storage.contracts.engine import CandleQueryEngineContract
from backend.candle_storage.models.dataset import CandleQueryFilters
from backend.indicator_engine.engine.pipeline import IndicatorCalculationPipeline
from backend.indicator_engine.engine.engine import IndicatorEngine
from backend.indicator_engine.calculators.sma import SMACalculator

class DummyCandleQuery(CandleQueryEngineContract):
    async def query(self, filters: CandleQueryFilters) -> AsyncGenerator[Candle, None]:
        base_price = 100.0
        for i in range(20):
            yield Candle(
                symbol=filters.symbol,
                timeframe=filters.timeframe,
                timestamp=datetime(2023, 1, 1) + timedelta(days=i),
                open=str(base_price),
                high=str(base_price + 1),
                low=str(base_price - 1),
                close=str(base_price),
                volume="1000"
            )

class DummyIndicatorRepo:
    def __init__(self):
        self.saved = []
    
    async def save_batch(self, indicators):
        self.saved.extend(indicators)

@pytest.mark.asyncio
async def test_indicator_pipeline():
    repo = DummyIndicatorRepo()
    query_engine = DummyCandleQuery()
    
    engine = IndicatorEngine([SMACalculator()])
    pipeline = IndicatorCalculationPipeline(
        candle_query_engine=query_engine,
        indicator_repository=repo,
        indicator_engine=engine
    )
    
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    results = await pipeline.run(symbol, Timeframe.D1, "canonical", incremental=False)
    
    assert len(results) == 7 # 20 candles, SMA 14 -> 7 results
    assert len(repo.saved) == 7
