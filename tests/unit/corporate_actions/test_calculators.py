import pytest
from datetime import datetime
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.corporate_actions.models.action import CorporateAction, ActionType
from backend.corporate_actions.adjustment.calculators import (
    SplitAdjustment, ReverseSplitAdjustment, BonusAdjustment, DividendAdjustment
)

@pytest.fixture
def base_candle():
    sym = SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))
    return Candle(
        symbol=sym,
        timeframe=Timeframe.D1,
        timestamp=datetime(2024, 1, 1),
        open=100.0,
        high=105.0,
        low=95.0,
        close=100.0,
        volume=1001,
        is_completed=True
    )

@pytest.fixture
def split_action():
    sym = SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))
    return CorporateAction(
        symbol=sym,
        action_type=ActionType.STOCK_SPLIT,
        effective_date=datetime(2024, 1, 2).date(),
        ratio=2.0 # 2:1 split
    )

@pytest.fixture
def reverse_split_action():
    sym = SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))
    return CorporateAction(
        symbol=sym,
        action_type=ActionType.REVERSE_SPLIT,
        effective_date=datetime(2024, 1, 2).date(),
        ratio=0.5 # 1:2 reverse split
    )

@pytest.fixture
def dividend_action():
    sym = SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))
    return CorporateAction(
        symbol=sym,
        action_type=ActionType.CASH_DIVIDEND,
        effective_date=datetime(2024, 1, 2).date(),
        amount=10.0
    )

def test_split_adjustment(base_candle, split_action):
    calc = SplitAdjustment()
    adj = calc.adjust(base_candle, split_action)
    
    # 2:1 split
    assert adj.open == 50.0
    assert adj.high == 52.5
    assert adj.low == 47.5
    assert adj.close == 50.0
    # Volume is 1001 * 2 = 2002
    assert adj.volume == 2002

def test_reverse_split_adjustment(base_candle, reverse_split_action):
    calc = ReverseSplitAdjustment()
    adj = calc.adjust(base_candle, reverse_split_action)
    
    # 1:2 reverse split (ratio = 0.5)
    assert adj.open == 200.0
    assert adj.high == 210.0
    assert adj.low == 190.0
    assert adj.close == 200.0
    # Volume is 1001 * 0.5 = 500.5 -> 500 (deterministic integer rounding)
    assert adj.volume == 500

def test_proportional_dividend_adjustment(base_candle, dividend_action):
    # Close price prior to ex-date was 100.0. Dividend is 10.0.
    # Multiplier = 1 - (10.0 / 100.0) = 0.9
    calc = DividendAdjustment(close_prior_to_ex_date=100.0)
    adj = calc.adjust(base_candle, dividend_action)
    
    assert adj.open == 90.0
    assert adj.high == 94.5
    assert adj.low == 85.5
    assert adj.close == 90.0
    # Volume is unaffected
    assert adj.volume == 1001

def test_proportional_dividend_zero_or_negative_price(base_candle, dividend_action):
    calc = DividendAdjustment(close_prior_to_ex_date=0.0)
    adj = calc.adjust(base_candle, dividend_action)
    # Should not adjust if prior close is <= 0
    assert adj.close == 100.0
