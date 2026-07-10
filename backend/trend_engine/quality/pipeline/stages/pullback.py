"""
Trend Quality Stage: Pullback
=============================

Evaluates mathematical pullback behavior of the trend.
"""

from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.models.models import PullbackQualityResult
from backend.trend_engine.contracts.contracts import IStructureProvider
from backend.trend_engine.models.models import TrendDirection

class PullbackQualityStage(ITrendQualityStage):
    """
    Evaluates depth and duration of pullbacks against the primary trend.
    Metrics:
      - average_pullback_depth_percent
      - average_pullback_duration_bars
      - pullback_count
      - deepest_pullback_percent
    """
    
    def __init__(self, structure_provider: IStructureProvider):
        self._provider = structure_provider
        
    async def execute(self, context: QualityExecutionContext) -> None:
        structure_snapshot_id = context.parent_snapshot.source_structure_snapshot_id
        
        for ts in context.parent_snapshot.symbols:
            symbol_key = f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}"
            symbol_context = context.symbol_contexts.get(symbol_key)
            if not symbol_context:
                continue
                
            if ts.direction in [TrendDirection.UNKNOWN, TrendDirection.SIDEWAYS]:
                symbol_context.pullback_result = PullbackQualityResult(
                    average_pullback_depth_percent=0.0,
                    average_pullback_duration_bars=0.0,
                    pullback_count=0,
                    deepest_pullback_percent=0.0
                )
                continue
                
            try:
                # Simulating pullback depth extraction from structure points
                structures = await self._provider.get_latest_structures(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=structure_snapshot_id,
                    limit=20
                )
                
                if len(structures) < 2:
                    symbol_context.pullback_result = PullbackQualityResult(
                        average_pullback_depth_percent=0.0,
                        average_pullback_duration_bars=0.0,
                        pullback_count=0,
                        deepest_pullback_percent=0.0
                    )
                    continue
                
                pullback_depths = []
                pullback_durations = []
                
                # Pairwise comparison to find contra-trend moves
                for i in range(1, len(structures)):
                    curr = structures[i-1] # newer
                    prev = structures[i]   # older
                    
                    depth = 0.0
                    if ts.direction == TrendDirection.UPTREND and curr.swing_point.price < prev.swing_point.price:
                        # Pullback in uptrend
                        depth = (prev.swing_point.price - curr.swing_point.price) / prev.swing_point.price
                    elif ts.direction == TrendDirection.DOWNTREND and curr.swing_point.price > prev.swing_point.price:
                        # Pullback in downtrend
                        depth = (curr.swing_point.price - prev.swing_point.price) / prev.swing_point.price
                        
                    if depth > 0:
                        pullback_depths.append(depth * 100.0)
                        # Simplistic duration approximation based on structure index difference
                        pullback_durations.append(float(abs(curr.swing_point.timestamp.timestamp() - prev.swing_point.timestamp.timestamp()) / 86400.0))
                
                count = len(pullback_depths)
                avg_depth = sum(pullback_depths) / count if count > 0 else 0.0
                avg_duration = sum(pullback_durations) / count if count > 0 else 0.0
                max_depth = max(pullback_depths) if count > 0 else 0.0
                
                symbol_context.pullback_result = PullbackQualityResult(
                    average_pullback_depth_percent=round(avg_depth, 2),
                    average_pullback_duration_bars=round(avg_duration, 2),
                    pullback_count=count,
                    deepest_pullback_percent=round(max_depth, 2)
                )
                
            except Exception as e:
                context.warnings.append(f"Pullback evaluation failed for {symbol_key}: {e}")
                symbol_context.pullback_result = PullbackQualityResult(
                    average_pullback_depth_percent=0.0,
                    average_pullback_duration_bars=0.0,
                    pullback_count=0,
                    deepest_pullback_percent=0.0
                )
