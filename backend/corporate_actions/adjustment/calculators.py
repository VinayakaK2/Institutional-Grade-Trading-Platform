import math

from backend.market_data.models.candle import Candle
from backend.corporate_actions.models.action import CorporateAction

class BaseAdjustment:
    def adjust(self, candle: Candle, action: CorporateAction) -> Candle:
        raise NotImplementedError

class SplitAdjustment(BaseAdjustment):
    """
    Adjusts candles for a stock split.
    Prices are divided by the split ratio.
    Volume is multiplied by the split ratio (rounded to int).
    """
    def adjust(self, candle: Candle, action: CorporateAction) -> Candle:
        ratio = action.ratio
        if not ratio or ratio <= 0:
            return candle
            
        return Candle(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open / ratio,
            high=candle.high / ratio,
            low=candle.low / ratio,
            close=candle.close / ratio,
            volume=math.floor(candle.volume * ratio), # Deterministic integer rounding policy
            is_completed=candle.is_completed
        )

class ReverseSplitAdjustment(BaseAdjustment):
    """
    Adjusts candles for a reverse stock split.
    Prices are divided by the split ratio (which is < 1).
    Volume is multiplied by the split ratio (rounded to int).
    """
    def adjust(self, candle: Candle, action: CorporateAction) -> Candle:
        ratio = action.ratio
        if not ratio or ratio <= 0:
            return candle
            
        return Candle(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open / ratio,
            high=candle.high / ratio,
            low=candle.low / ratio,
            close=candle.close / ratio,
            volume=math.floor(candle.volume * ratio), # Deterministic integer rounding policy
            is_completed=candle.is_completed
        )

class BonusAdjustment(BaseAdjustment):
    """
    Adjusts candles for a bonus issue.
    Works mathematically similar to a stock split.
    """
    def adjust(self, candle: Candle, action: CorporateAction) -> Candle:
        ratio = action.ratio
        if not ratio or ratio <= 0:
            return candle
            
        return Candle(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open / ratio,
            high=candle.high / ratio,
            low=candle.low / ratio,
            close=candle.close / ratio,
            volume=math.floor(candle.volume * ratio), # Deterministic integer rounding policy
            is_completed=candle.is_completed
        )

class DividendAdjustment(BaseAdjustment):
    """
    Adjusts candles for a cash dividend using proportional ratio adjustment.
    The ratio is calculated as: 1 - (Dividend Amount / Close Price prior to ex-date).
    Because we process backwards, we apply this multiplier to all prices before the effective date.
    Volume is unaffected.
    """
    def __init__(self, close_prior_to_ex_date: float):
        self.close_prior = close_prior_to_ex_date
        
    def adjust(self, candle: Candle, action: CorporateAction) -> Candle:
        amount = action.amount
        if not amount or amount <= 0 or self.close_prior <= 0:
            return candle
            
        # Proportional multiplier
        multiplier = max(0.0, 1.0 - (amount / self.close_prior))
        
        return Candle(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open * multiplier,
            high=candle.high * multiplier,
            low=candle.low * multiplier,
            close=candle.close * multiplier,
            volume=candle.volume, # Volume is not affected by cash dividends
            is_completed=candle.is_completed
        )
