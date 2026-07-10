"""
Trend Quality Stage: Normalization
==================================

Maps heterogeneous raw outputs (EMA distances, pullback counts, ages) 
into a consistent, unitless normalized representation suitable for deterministic aggregation.
"""

from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.models.models import NormalizedQualityMetrics

class TrendNormalizationStage(ITrendQualityStage):
    """
    Normalizes the raw metrics of prior stages to a 0.0 - 1.0 scale.
    """
    
    async def execute(self, context: QualityExecutionContext) -> None:
        
        for ts in context.parent_snapshot.symbols:
            symbol_key = f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}"
            symbol_context = context.symbol_contexts.get(symbol_key)
            if not symbol_context:
                continue
                
            try:
                s_res = symbol_context.strength_result
                c_res = symbol_context.consistency_result
                pb_res = symbol_context.pullback_result
                p_res = symbol_context.persistence_result
                
                # If any of the independent stages failed to produce output, normalization defaults to 0
                if not s_res or not c_res or not pb_res or not p_res:
                    symbol_context.normalized_metrics = NormalizedQualityMetrics(
                        normalized_strength=0.0,
                        normalized_consistency=0.0,
                        normalized_pullback_quality=0.0,
                        normalized_persistence=0.0
                    )
                    continue
                
                # 1. Normalize Strength
                raw_sep = s_res.ema_separation_ratio
                max_sep = context.config.max_ema_separation_ratio
                norm_strength = min(raw_sep / max_sep, 1.0) if max_sep > 0 else 0.0
                
                # 2. Normalize Consistency
                norm_consistency = c_res.sequence_stability_ratio
                
                # 3. Normalize Pullback
                raw_depth = pb_res.average_pullback_depth_percent / 100.0
                max_depth = context.config.max_pullback_depth_percent
                norm_pullback = max(0.0, 1.0 - (raw_depth / max_depth)) if max_depth > 0 else 0.0
                
                # 4. Normalize Persistence
                raw_age = p_res.trend_age_bars
                mature_age = context.config.mature_trend_age_bars
                norm_persistence = min(raw_age / mature_age, 1.0) if mature_age > 0 else 0.0
                
                symbol_context.normalized_metrics = NormalizedQualityMetrics(
                    normalized_strength=round(norm_strength, 4),
                    normalized_consistency=round(norm_consistency, 4),
                    normalized_pullback_quality=round(norm_pullback, 4),
                    normalized_persistence=round(norm_persistence, 4)
                )
                
            except Exception as e:
                context.warnings.append(f"Normalization failed for {symbol_key}: {e}")
                symbol_context.normalized_metrics = NormalizedQualityMetrics(
                    normalized_strength=0.0,
                    normalized_consistency=0.0,
                    normalized_pullback_quality=0.0,
                    normalized_persistence=0.0
                )
