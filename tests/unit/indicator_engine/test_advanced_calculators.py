import pytest
from datetime import datetime, timezone, timedelta
from typing import List
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.indicator_engine.models.indicator import IndicatorType
from backend.indicator_engine.calculators.vwap import VWAPCalculator
from backend.indicator_engine.calculators.bollinger import BollingerBandsCalculator
from backend.indicator_engine.calculators.supertrend import SuperTrendCalculator
from backend.indicator_engine.calculators.obv import OBVCalculator
from backend.indicator_engine.calculators.cmf import CMFCalculator

@pytest.fixture
def sample_candles() -> List[Candle]:
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    # Simple deterministic up-trend then down-trend
    prices = [
        (10.0, 15.0, 8.0, 12.0, 100.0),
        (12.0, 16.0, 11.0, 14.0, 150.0),
        (14.0, 18.0, 13.0, 16.0, 200.0),
        (16.0, 17.0, 15.0, 15.0, 100.0), # Doji-like
        (15.0, 16.0, 10.0, 11.0, 300.0), # Down
        (11.0, 12.0, 7.0, 8.0, 250.0),   # Down
        (8.0, 10.0, 5.0, 9.0, 400.0),    # Reversal
    ]
    
    candles = []
    for i, (o, h, l, c, v) in enumerate(prices):
        candles.append(
            Candle(
                symbol=sym,
                timeframe=tf,
                timestamp=base_time + timedelta(days=i),
                open=o,
                high=h,
                low=l,
                close=c,
                volume=v
            )
        )
    return candles

def test_vwap_calculator(sample_candles):
    calc = VWAPCalculator()
    
    # Two sessions: 0-3 is session1, 4-6 is session2
    sessions = ["s1", "s1", "s1", "s1", "s2", "s2", "s2"]
    
    res = calc.calculate(sample_candles, "CANONICAL", session_identifiers=sessions)
    
    assert len(res) == len(sample_candles)
    
    # Verify first candle
    c1 = sample_candles[0]
    typ_1 = (float(c1.high) + float(c1.low) + float(c1.close)) / 3.0
    assert res[0].value == pytest.approx(typ_1)
    
    # Session reset on index 4
    c5 = sample_candles[4]
    typ_5 = (float(c5.high) + float(c5.low) + float(c5.close)) / 3.0
    assert res[4].value == pytest.approx(typ_5)
    
    assert res[0].indicator_type == IndicatorType.VWAP

def test_vwap_missing_sessions(sample_candles):
    calc = VWAPCalculator()
    with pytest.raises(ValueError):
        calc.calculate(sample_candles, "CANONICAL")

def test_bollinger_bands_calculator(sample_candles):
    calc = BollingerBandsCalculator()
    # Use period=3 for testing short window
    res = calc.calculate(sample_candles, "CANONICAL", period=3, std_dev_multiplier=2.0)
    
    # First 2 should be skipped because period=3 requires 3 candles
    assert len(res) == 5
    
    # Third candle (index 2) closes: 12, 14, 16 -> mean=14.0
    # variance = ((12-14)**2 + (14-14)**2 + (16-14)**2)/3 = (4 + 0 + 4)/3 = 8/3 = 2.666...
    # std_dev = sqrt(2.666...) = 1.63299
    # upper = 14 + 2 * 1.63299 = 17.26598
    # lower = 14 - 2 * 1.63299 = 10.73401
    
    first_res = res[0]
    assert first_res.value == 14.0 # middle band
    assert "upper_band" in first_res.outputs
    assert "lower_band" in first_res.outputs
    assert abs(first_res.outputs["upper_band"] - 17.26598) < 0.001

def test_supertrend_calculator(sample_candles):
    calc = SuperTrendCalculator()
    # period=3 to ensure some output
    res = calc.calculate(sample_candles, "CANONICAL", atr_period=3, multiplier=3.0)
    
    assert len(res) > 0
    
    for r in res:
        assert r.indicator_type == IndicatorType.SUPERTREND
        assert "upper_band" in r.outputs
        assert "lower_band" in r.outputs
        assert "trend_direction" in r.outputs
        assert r.outputs["trend_direction"] in [1.0, -1.0]
        # value is the active band
        assert r.value == r.outputs["lower_band"] if r.outputs["trend_direction"] == 1.0 else r.outputs["upper_band"]

def test_obv_calculator(sample_candles):
    calc = OBVCalculator()
    res = calc.calculate(sample_candles, "CANONICAL")
    
    assert len(res) == len(sample_candles)
    
    # OBV starts at 0 since there's no prior close. 
    # Wait, the first candle has no prior close, so OBV = 0.
    assert res[0].value == 0.0
    
    # 2nd close(14) > 1st close(12). vol=150. OBV = 150
    assert res[1].value == 150.0
    
    # 3rd close(16) > 14. vol=200. OBV = 350
    assert res[2].value == 350.0

def test_cmf_calculator(sample_candles):
    calc = CMFCalculator()
    # period=3
    res = calc.calculate(sample_candles, "CANONICAL", period=3)
    
    # Expect 5 outputs for period=3 (candles length 7 -> 7 - 3 + 1)
    assert len(res) == 5
    
    # Validate the first CMF result (covers index 0,1,2)
    # CMF = sum(MFV) / sum(Vol) over last 3
    # c0: H=15, L=8, C=12 -> MFM = ((12-8) - (15-12)) / (15-8) = (4 - 3)/7 = 1/7. Vol=100. MFV = 100/7
    # c1: H=16, L=11, C=14 -> MFM = ((14-11) - (16-14)) / (16-11) = (3 - 2)/5 = 1/5. Vol=150. MFV = 150/5 = 30
    # c2: H=18, L=13, C=16 -> MFM = ((16-13) - (18-16)) / (18-13) = (3 - 2)/5 = 1/5. Vol=200. MFV = 200/5 = 40
    # Sum(MFV) = 14.2857 + 30 + 40 = 84.2857
    # Sum(Vol) = 100 + 150 + 200 = 450
    # CMF = 84.2857 / 450 = 0.1873
    
    first_cmf = res[0].value
    assert abs(first_cmf - 0.1873) < 0.001
