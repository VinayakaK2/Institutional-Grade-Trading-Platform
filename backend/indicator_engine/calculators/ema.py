from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class EMACalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.EMA

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[IndicatorResult]:
        period = kwargs.get("period", 14)
        if period <= 0:
            raise ValueError("EMA period must be > 0")
            
        prices = self._extract_prices(candles, "close")
        results = []
        multiplier = 2 / (period + 1)
        
        if previous_state is not None:
            # Incremental calculation
            if "ema" not in previous_state:
                raise ValueError("Incremental EMA requires 'ema' in previous_state.")
            if not candles:
                return []
                
            current_ema = previous_state["ema"]
            
            for i in range(len(prices)):
                price = prices[i]
                current_ema = (price - current_ema) * multiplier + current_ema
                
                candle = candles[i]
                results.append(IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={"period": period},
                    value=current_ema,
                    internal_state={"ema": current_ema}
                ))
            return results
            
        # Full calculation
        self._validate_candles(candles, period)
        
        # The first EMA is typically seeded with an SMA of the first `period` elements
        sma_seed = sum(prices[:period]) / period
        
        current_ema = sma_seed
        
        # We emit the first EMA at index `period - 1` (the end of the SMA seed window)
        results.append(IndicatorResult(
            symbol=candles[period - 1].symbol,
            timeframe=candles[period - 1].timeframe,
            dataset_version=dataset_version,
            timestamp=candles[period - 1].timestamp,
            indicator_type=self.indicator_type,
            parameters={"period": period},
            value=current_ema,
            internal_state={"ema": current_ema}
        ))
        
        for i in range(period, len(prices)):
            price = prices[i]
            current_ema = (price - current_ema) * multiplier + current_ema
            
            candle = candles[i]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=current_ema,
                internal_state={"ema": current_ema}
            ))
            
        return results

class VolumeEMACalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VOL_EMA

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[IndicatorResult]:
        period = kwargs.get("period", 20)
        if period <= 0:
            raise ValueError("Volume EMA period must be > 0")
            
        volumes = self._extract_prices(candles, "volume")
        results = []
        multiplier = 2 / (period + 1)
        
        if previous_state is not None:
            if "ema" not in previous_state:
                raise ValueError("Incremental Volume EMA requires 'ema' in previous_state.")
            if not candles:
                return []
                
            current_ema = previous_state["ema"]
            
            for i in range(len(volumes)):
                volume = volumes[i]
                current_ema = (volume - current_ema) * multiplier + current_ema
                
                candle = candles[i]
                results.append(IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={"period": period},
                    value=current_ema,
                    internal_state={"ema": current_ema}
                ))
            return results
            
        self._validate_candles(candles, period)
        
        sma_seed = sum(volumes[:period]) / period
        current_ema = sma_seed
        
        results.append(IndicatorResult(
            symbol=candles[period - 1].symbol,
            timeframe=candles[period - 1].timeframe,
            dataset_version=dataset_version,
            timestamp=candles[period - 1].timestamp,
            indicator_type=self.indicator_type,
            parameters={"period": period},
            value=current_ema,
            internal_state={"ema": current_ema}
        ))
        
        for i in range(period, len(volumes)):
            volume = volumes[i]
            current_ema = (volume - current_ema) * multiplier + current_ema
            
            candle = candles[i]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=current_ema,
                internal_state={"ema": current_ema}
            ))
            
        return results
