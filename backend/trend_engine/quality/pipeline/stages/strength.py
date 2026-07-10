"""
Trend Quality Stage: Strength
=============================

Evaluates mathematical trend strength (EMA separation, continuity, direction stability).
"""

from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.models.models import TrendStrengthResult
from backend.trend_engine.contracts.contracts import IIndicatorProvider
from backend.trend_engine.models.models import TrendDirection

class TrendStrengthStage(ITrendQualityStage):
    """
    Evaluates objective mathematical strength of the trend.
    Metrics:
      - ema_separation_ratio: Percentage difference between fast and slow EMAs.
      - direction_stability_percent: Measure of how consistently EMAs are moving in the trend direction.
      - is_extended: True if EMA separation exceeds configuration max thresholds.
    """
    
    def __init__(self, indicator_provider: IIndicatorProvider):
        self._provider = indicator_provider
        
    async def execute(self, context: QualityExecutionContext) -> None:
        indicator_snapshot_id = context.parent_snapshot.source_indicator_snapshot_id
        
        for ts in context.parent_snapshot.symbols:
            symbol_key = f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}"
            symbol_context = context.symbol_contexts.get(symbol_key)
            if not symbol_context:
                continue
                
            if ts.direction in [TrendDirection.UNKNOWN, TrendDirection.SIDEWAYS]:
                # Non-trending symbols have 0 strength
                symbol_context.strength_result = TrendStrengthResult(
                    ema_separation_ratio=0.0,
                    direction_stability_percent=0.0,
                    is_extended=False
                )
                continue
                
            try:
                emas = await self._provider.get_ema_indicators(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=indicator_snapshot_id,
                    periods=[20, 50, 200]
                )
                
                if 20 not in emas or 50 not in emas or 200 not in emas:
                    raise ValueError("Missing required EMAs for strength evaluation.")
                    
                ema20 = emas[20].value
                ema50 = emas[50].value
                ema200 = emas[200].value
                
                # Separation ratio (using 20 and 200) relative to 200
                separation_ratio = abs(ema20 - ema200) / ema200 if ema200 > 0 else 0.0
                
                # Simple direction stability proxy: are 20 and 50 both on the expected side of 200?
                # This could be more advanced (e.g. slopes), but this satisfies Phase 7.3 math requirements.
                stability = 0.0
                if ts.direction == TrendDirection.UPTREND:
                    if ema20 > ema50 > ema200:
                        stability = 100.0
                    elif ema20 > ema200 and ema50 > ema200:
                        stability = 50.0
                elif ts.direction == TrendDirection.DOWNTREND:
                    if ema20 < ema50 < ema200:
                        stability = 100.0
                    elif ema20 < ema200 and ema50 < ema200:
                        stability = 50.0
                        
                is_extended = separation_ratio > context.config.max_ema_separation_ratio
                
                symbol_context.strength_result = TrendStrengthResult(
                    ema_separation_ratio=round(separation_ratio, 6),
                    direction_stability_percent=stability,
                    is_extended=is_extended
                )
                
            except Exception as e:
                context.warnings.append(f"Strength evaluation failed for {symbol_key}: {e}")
                symbol_context.strength_result = TrendStrengthResult(
                    ema_separation_ratio=0.0,
                    direction_stability_percent=0.0,
                    is_extended=False
                )
