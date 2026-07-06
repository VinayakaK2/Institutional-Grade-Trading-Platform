import pytest
from datetime import datetime
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.indicator_engine.calculators.sma import SMACalculator, VolumeSMACalculator
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.rsi import RSICalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.calculators.atr import ATRCalculator
from backend.indicator_engine.calculators.adx import ADXCalculator

def get_test_candles(num_candles: int = 50) -> list:
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    candles = []
    # Generate some pseudo-random but deterministic candle data
    base_price = 100.0
    for i in range(num_candles):
        # Creates a slight uptrend with some volatility
        open_p = base_price + i
        close_p = open_p + (1 if i % 2 == 0 else -0.5)
        high_p = max(open_p, close_p) + 1.0
        low_p = min(open_p, close_p) - 1.0
        
        candles.append(Candle(
            symbol=symbol,
            timeframe=tf,
            timestamp=datetime(2023, 1, 1).replace(day=(i % 28) + 1),
            open=str(open_p),
            high=str(high_p),
            low=str(low_p),
            close=str(close_p),
            volume=str(1000 + i * 100)
        ))
    
    # Sort candles to ensure strictly ascending chronological order
    # (Since we just looped over days of month, they might wrap. Let's fix that)
    from datetime import timedelta
    for i, c in enumerate(candles):
        c.timestamp = datetime(2023, 1, 1) + timedelta(days=i)
        
    return candles

def test_sma_calculator():
    calc = SMACalculator()
    candles = get_test_candles(20)
    
    # Period 14 should produce 20 - 14 + 1 = 7 results
    results = calc.calculate(candles, dataset_version="CANONICAL", period=14)
    assert len(results) == 7
    assert results[0].parameters["period"] == 14
    
def test_volume_sma_calculator():
    calc = VolumeSMACalculator()
    candles = get_test_candles(30)
    results = calc.calculate(candles, dataset_version="CANONICAL", period=20)
    assert len(results) == 11

def test_ema_calculator():
    calc = EMACalculator()
    candles = get_test_candles(20)
    results = calc.calculate(candles, dataset_version="CANONICAL", period=14)
    assert len(results) == 7
    
    # Test incremental
    prev_state = {"ema": 105.0}
    # For incremental, passing the last 2 candles should result in 2 EMA values
    incremental_results = calc.calculate(candles[-2:], dataset_version="CANONICAL", previous_state=prev_state, period=14)
    assert len(incremental_results) == 2

def test_rsi_calculator():
    calc = RSICalculator()
    candles = get_test_candles(20)
    results = calc.calculate(candles, dataset_version="CANONICAL", period=14)
    # 20 candles, period 14, needs 14+1=15 candles for first result. 
    # Total results: 20 - 15 + 1 = 6
    assert len(results) == 6
    assert 0 <= results[-1].value <= 100

def test_macd_calculator():
    calc = MACDCalculator()
    candles = get_test_candles(50)
    results = calc.calculate(candles, dataset_version="CANONICAL", fast_period=12, slow_period=26, signal_period=9)
    # MACD produces 3 outputs per candle
    # First valid MACD is at slow_period - 1 = 25
    # First valid signal is at 25 + 9 - 1 = 33
    # Total valid candles = 50 - 33 = 17
    # 17 candles * 3 outputs = 51 results
    assert len(results) == 51

def test_atr_calculator():
    calc = ATRCalculator()
    candles = get_test_candles(20)
    results = calc.calculate(candles, dataset_version="CANONICAL", period=14)
    # TR needs 1 prev candle. ATR needs 14 TRs. First ATR at index 14. 
    assert len(results) == 6

def test_adx_calculator():
    calc = ADXCalculator()
    candles = get_test_candles(40)
    results = calc.calculate(candles, dataset_version="CANONICAL", period=14)
    # ADX requires 2*period = 28 candles. First result at index 28.
    # Total valid candles = 40 - 28 = 12
    # 3 outputs (ADX, DI+, DI-) * 12 = 36
    assert len(results) == 36
