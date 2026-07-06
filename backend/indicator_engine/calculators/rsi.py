from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class RSICalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.RSI

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        period = kwargs.get("period", 14)
        if period <= 0:
            raise ValueError("RSI period must be > 0")
            
        # We need period + 1 candles to get `period` differences
        self._validate_candles(candles, period + 1)
        
        prices = self._extract_prices(candles, "close")
        results = []
        
        # Calculate initial average gain/loss over the first `period` steps
        gains = []
        losses = []
        
        for i in range(1, period + 1):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))
                
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        def calc_rsi(ag, al):
            if al == 0:
                return 100.0
            rs = ag / al
            return 100.0 - (100.0 / (1.0 + rs))

        # First RSI value
        current_rsi = calc_rsi(avg_gain, avg_loss)
        results.append(IndicatorResult(
            symbol=candles[period].symbol,
            timeframe=candles[period].timeframe,
            dataset_version=dataset_version,
            timestamp=candles[period].timestamp,
            indicator_type=self.indicator_type,
            parameters={"period": period},
            value=current_rsi
        ))
        
        # Smoothed calculation for the rest
        for i in range(period + 1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gain = change
                loss = 0.0
            else:
                gain = 0.0
                loss = abs(change)
                
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            current_rsi = calc_rsi(avg_gain, avg_loss)
            
            candle = candles[i]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=current_rsi
            ))
            
        return results
