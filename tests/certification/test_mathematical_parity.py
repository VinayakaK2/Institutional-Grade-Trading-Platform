import math
import pytest
from backend.indicator_engine.calculators.sma import SMACalculator
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.rsi import RSICalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.calculators.atr import ATRCalculator
from backend.indicator_engine.calculators.bollinger import BollingerBandsCalculator
from backend.indicator_engine.models.indicator import IndicatorType

from tests.certification.utils import (
    generate_linear_candles, 
    generate_alternating_candles,
    assert_floats_close
)

def test_sma_mathematical_parity():
    """
    Formula: SUM(Close, N) / N
    Data: Linear dataset (100, 101, 102...)
    If N=5, at index 4 (values 100..104), sum is 510, SMA is 102.
    """
    candles = generate_linear_candles(10, start_price=100.0, step=1.0)
    calc = SMACalculator()
    results = calc.calculate(candles, "v1", period=5)
    
    assert len(results) == 6
    
    # Check value at index 0 (which corresponds to candle index 4)
    assert_floats_close(102.0, results[0].value, msg="SMA Period 5 initial value")
    # Check value at index 5 (which corresponds to candle index 9) -> sum = 535 -> SMA = 107
    assert_floats_close(107.0, results[-1].value, msg="SMA Period 5 final value")

def test_ema_mathematical_parity():
    """
    Formula: Value * (2 / (N + 1)) + Previous_EMA * (1 - (2 / (N + 1)))
    Initial EMA is SMA of first N values.
    """
    candles = generate_linear_candles(10, start_price=100.0, step=1.0)
    calc = EMACalculator()
    results = calc.calculate(candles, "v1", period=5)
    
    # At index 0 (candle index 4), initial EMA = SMA = 102
    assert_floats_close(102.0, results[0].value, msg="EMA Period 5 initial value")
    
    # At index 1 (candle index 5), close = 105. Multiplier = 2/6 = 0.33333333
    # EMA = 105 * (1/3) + 102 * (2/3) = 35 + 68 = 103
    assert_floats_close(103.0, results[1].value, msg="EMA Period 5 second value")
    
    # At index 2 (candle index 6), close = 106. EMA = 106 * (1/3) + 103 * (2/3) = 35.3333333 + 68.6666666 = 104
    assert_floats_close(104.0, results[2].value, msg="EMA Period 5 third value")

def test_rsi_mathematical_parity():
    """
    RSI = 100 - (100 / (1 + RS)), RS = Smoothed Avg Gain / Smoothed Avg Loss.
    We test on an alternating dataset to check both gains and losses.
    """
    # 100 -> 105 (gain 5) -> 95 (loss 10) -> 100 (gain 5)
    # Actually, our alternating candles go:
    # i=0: 100 -> 105
    # i=1: 100 -> 95
    # i=2: 100 -> 105
    # Let's just use manual price series to make it exactly deterministic.
    from backend.market_data.models.candle import Candle
    from backend.market_data.models.symbol import SymbolReference, ExchangeReference
    from backend.market_data.models.timeframe import Timeframe
    from datetime import datetime, timezone, timedelta
    
    prices = [100.0, 102.0, 101.0, 103.0, 100.0, 99.0, 98.0, 101.0]
    symbol = SymbolReference(symbol="TEST/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    candles = [Candle(
        symbol=symbol, timeframe=Timeframe.H1, timestamp=datetime(2025,1,1,tzinfo=timezone.utc)+timedelta(hours=i),
        open=p, high=p, low=p, close=p, volume=1000.0
    ) for i, p in enumerate(prices)]
    
    calc = RSICalculator()
    results = calc.calculate(candles, "v1", period=4)
    
    # Gains: [N/A, 2.0, 0.0, 2.0, 0.0, 0.0, 0.0, 3.0]
    # Losses: [N/A, 0.0, 1.0, 0.0, 3.0, 1.0, 1.0, 0.0]
    # Period = 4. 
    # First 4 deltas (indices 1 to 4):
    # Gains: 2.0, 0.0, 2.0, 0.0 -> Avg Gain = 1.0
    # Losses: 0.0, 1.0, 0.0, 3.0 -> Avg Loss = 1.0
    # RS = 1.0, RSI = 50.0 at index 0 (candle index 4)
    
    assert_floats_close(50.0, results[0].value, msg="RSI Period 4 initial value")
    
    # Index 1 (candle index 5) (delta -1, so gain 0, loss 1)
    # Smoothed Avg Gain = (1.0 * 3 + 0) / 4 = 0.75
    # Smoothed Avg Loss = (1.0 * 3 + 1) / 4 = 1.0
    # RS = 0.75, RSI = 100 - (100 / 1.75) = 100 - 57.142857 = 42.8571428
    assert_floats_close(42.857142857142854, results[1].value, msg="RSI Period 4 at index 5")

def test_macd_mathematical_parity():
    """
    MACD = FastEMA - SlowEMA
    Signal = EMA(MACD, SignalPeriod)
    Histogram = MACD - Signal
    """
    candles = generate_linear_candles(50, start_price=100.0, step=1.0)
    calc = MACDCalculator()
    results = calc.calculate(candles, "v1", fast_period=12, slow_period=26, signal_period=9)
    
    # Just verify that Histogram = MACD - Signal exactly
    macds = {r.timestamp: r.value for r in results if r.indicator_type == IndicatorType.MACD}
    signals = {r.timestamp: r.value for r in results if r.indicator_type == IndicatorType.MACD_SIGNAL}
    hists = {r.timestamp: r.value for r in results if r.indicator_type == IndicatorType.MACD_HISTOGRAM}
    
    for ts in macds.keys():
        if not math.isnan(macds[ts]) and not math.isnan(signals[ts]):
            assert_floats_close(macds[ts] - signals[ts], hists[ts], msg=f"MACD Histogram Math at {ts}")

def test_atr_mathematical_parity():
    """
    True Range = max(High - Low, abs(High - PrevClose), abs(Low - PrevClose))
    ATR = Smoothed Moving Average (RMA) of TR.
    Initial ATR = SMA(TR, period)
    """
    # Linear candles: step 1, High = P+1, Low = P-1, Close = P
    # TR: 
    # Current High - Current Low = (P+1) - (P-1) = 2.0
    # Current High - Prev Close = (P+1) - (P-1) = 2.0
    # Current Low - Prev Close = (P-1) - (P-1) = 0
    # TR is always 2.0!
    # So ATR should perfectly converge to 2.0
    candles = generate_linear_candles(20, start_price=100.0, step=1.0)
    calc = ATRCalculator()
    results = calc.calculate(candles, "v1", period=14)
    
    assert_floats_close(2.0, results[-1].value, msg="ATR Period 14 for constant TR 2.0")
