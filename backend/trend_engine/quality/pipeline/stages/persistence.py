"""
Trend Quality Stage: Persistence
================================

Evaluates how long the trend has been sustained.
"""

from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.models.models import TrendPersistenceResult
from backend.trend_engine.contracts.contracts import IStructureProvider
from backend.trend_engine.models.models import TrendDirection
from datetime import datetime, timezone

class TrendPersistenceStage(ITrendQualityStage):
    """
    Evaluates trend age and continuity.
    Metrics:
      - trend_age_bars
      - interruption_count
      - longest_uninterrupted_run_bars
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
                symbol_context.persistence_result = TrendPersistenceResult(
                    trend_age_bars=0,
                    interruption_count=0,
                    longest_uninterrupted_run_bars=0
                )
                continue
                
            try:
                # Simulating age extraction
                structures = await self._provider.get_latest_structures(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=structure_snapshot_id,
                    limit=50
                )
                
                if len(structures) < 2:
                    symbol_context.persistence_result = TrendPersistenceResult(
                        trend_age_bars=0,
                        interruption_count=0,
                        longest_uninterrupted_run_bars=0
                    )
                    continue
                
                # Assume each structure point roughly correlates to some 'bars' distance. 
                # For real mathematical purposes, we use actual time elapsed in days as proxy for bars
                now_ts = datetime.now(timezone.utc).timestamp()
                oldest_ts = structures[-1].swing_point.timestamp.timestamp()
                
                age_bars = int((now_ts - oldest_ts) / 86400.0)
                
                # Interruptions: points moving against the trend
                interruptions = 0
                max_run = 0
                current_run = 0
                
                for i in range(1, len(structures)):
                    curr = structures[i-1] # newer
                    prev = structures[i]   # older
                    
                    is_favorable = False
                    if ts.direction == TrendDirection.UPTREND and curr.swing_point.price >= prev.swing_point.price:
                        is_favorable = True
                    elif ts.direction == TrendDirection.DOWNTREND and curr.swing_point.price <= prev.swing_point.price:
                        is_favorable = True
                        
                    if is_favorable:
                        current_run += 1
                        max_run = max(max_run, current_run)
                    else:
                        interruptions += 1
                        current_run = 0
                        
                symbol_context.persistence_result = TrendPersistenceResult(
                    trend_age_bars=age_bars,
                    interruption_count=interruptions,
                    longest_uninterrupted_run_bars=max_run
                )
                
            except Exception as e:
                context.warnings.append(f"Persistence evaluation failed for {symbol_key}: {e}")
                symbol_context.persistence_result = TrendPersistenceResult(
                    trend_age_bars=0,
                    interruption_count=0,
                    longest_uninterrupted_run_bars=0
                )
