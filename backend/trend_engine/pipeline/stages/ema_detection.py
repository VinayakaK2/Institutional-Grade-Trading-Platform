"""
EMA Structure Detection Stage
=============================

Retrieves EMA 20, 50, and 200 indicators and determines their structural alignment.
"""
import time
from backend.trend_engine.contracts.contracts import ITrendStage, IIndicatorProvider
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.models.models import TrendStageResult, TrendStageStatus

class EmaStructureDetectionStage(ITrendStage):
    """
    Evaluates Bullish or Bearish alignment of EMAs.
    No trend quality or strength is evaluated.
    """
    
    def __init__(self, provider: IIndicatorProvider):
        self._provider = provider
        
    @property
    def name(self) -> str:
        return "EmaStructureDetection"

    async def execute(self, context: TrendExecutionContext) -> TrendStageResult:
        start_time = time.time()
        warnings = []
        
        indicator_snapshot_id = context.source_indicator_snapshot_id
        if not indicator_snapshot_id:
            return TrendStageResult(
                stage_name=self.name,
                status=TrendStageStatus.FAILED,
                duration_ms=(time.time() - start_time) * 1000,
                warnings=["Missing source_indicator_snapshot_id in context."]
            )

        for ts in context.symbols:
            try:
                emas = await self._provider.get_ema_indicators(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=indicator_snapshot_id,
                    periods=[20, 50, 200]
                )
                
                if 20 not in emas or 50 not in emas or 200 not in emas:
                    # Missing data
                    ts.stage_metadata["ema_alignment"] = "UNKNOWN"
                    ts.stage_metadata["ema_error"] = "Missing one or more required EMAs (20, 50, 200)"
                    continue
                    
                ema20 = emas[20].value
                ema50 = emas[50].value
                ema200 = emas[200].value
                
                # Check for strictly greater/less
                if ema20 > ema50 and ema50 > ema200:
                    ts.stage_metadata["ema_alignment"] = "BULLISH"
                elif ema20 < ema50 and ema50 < ema200:
                    ts.stage_metadata["ema_alignment"] = "BEARISH"
                else:
                    ts.stage_metadata["ema_alignment"] = "INVALID"
                    
            except Exception as e:
                ts.stage_metadata["ema_alignment"] = "UNKNOWN"
                ts.stage_metadata["ema_error"] = str(e)
                warnings.append(f"Error processing {ts.watchlist_symbol.symbol.symbol}: {e}")

        return TrendStageResult(
            stage_name=self.name,
            status=TrendStageStatus.SUCCESS,
            duration_ms=(time.time() - start_time) * 1000,
            warnings=warnings
        )
