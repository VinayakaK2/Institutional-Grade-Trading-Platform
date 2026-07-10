"""
Trend Quality Stage: Consistency
================================

Evaluates mathematical consistency of the trend structure.
"""

from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.models.models import TrendConsistencyResult
from backend.trend_engine.contracts.contracts import IStructureProvider
from backend.trend_engine.models.models import TrendDirection

class TrendConsistencyStage(ITrendQualityStage):
    """
    Evaluates sequence stability and structural noise.
    Metrics:
      - sequence_stability_ratio: Percentage of valid HH/HL (or LH/LL) structures vs total structures.
      - structural_noise_percent: Percentage of invalid/noisy structures.
      - valid_structures_count: Raw count of aligned structures.
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
                symbol_context.consistency_result = TrendConsistencyResult(
                    sequence_stability_ratio=0.0,
                    structural_noise_percent=0.0,
                    valid_structures_count=0
                )
                continue
                
            try:
                structures = await self._provider.get_latest_structures(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=structure_snapshot_id,
                    limit=20
                )
                
                if len(structures) < context.config.min_structure_points_required:
                    symbol_context.consistency_result = TrendConsistencyResult(
                        sequence_stability_ratio=0.0,
                        structural_noise_percent=0.0,
                        valid_structures_count=len(structures)
                    )
                    continue
                
                valid_count = 0
                total_count = len(structures)
                
                # Simple stability heuristic based on sequential pairs
                for i in range(1, total_count):
                    curr = structures[i-1] # Newer
                    prev = structures[i]   # Older
                    
                    if ts.direction == TrendDirection.UPTREND:
                        if curr.swing_point.price > prev.swing_point.price:
                            valid_count += 1
                    elif ts.direction == TrendDirection.DOWNTREND:
                        if curr.swing_point.price < prev.swing_point.price:
                            valid_count += 1
                            
                stability_ratio = valid_count / (total_count - 1) if total_count > 1 else 0.0
                noise_percent = (1.0 - stability_ratio) * 100.0
                
                symbol_context.consistency_result = TrendConsistencyResult(
                    sequence_stability_ratio=round(stability_ratio, 4),
                    structural_noise_percent=round(noise_percent, 2),
                    valid_structures_count=valid_count
                )
                
            except Exception as e:
                context.warnings.append(f"Consistency evaluation failed for {symbol_key}: {e}")
                symbol_context.consistency_result = TrendConsistencyResult(
                    sequence_stability_ratio=0.0,
                    structural_noise_percent=0.0,
                    valid_structures_count=0
                )
