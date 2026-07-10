"""
Trend Resolution Stage
======================

Synthesizes EMA and Price Structure alignments into a final deterministic Trend Direction and State.
"""
import time
from backend.trend_engine.contracts.contracts import ITrendStage
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.models.models import TrendStageResult, TrendStageStatus, TrendDirection, TrendState

class TrendResolutionStage(ITrendStage):
    """
    Determines final trend direction and state deterministically.
    No probabilities or weighting.
    """
    
    @property
    def name(self) -> str:
        return "TrendResolution"

    async def execute(self, context: TrendExecutionContext) -> TrendStageResult:
        start_time = time.time()
        
        for ts in context.symbols:
            ema = ts.stage_metadata.get("ema_alignment", "UNKNOWN")
            structure = ts.stage_metadata.get("structure_alignment", "UNKNOWN")
            
            if ema == "UNKNOWN" or structure == "UNKNOWN":
                ts.direction = TrendDirection.UNKNOWN
                ts.state = TrendState.INCOMPLETE
            elif ema == "BULLISH" and structure == "BULLISH":
                ts.direction = TrendDirection.UPTREND
                ts.state = TrendState.VALID
            elif ema == "BEARISH" and structure == "BEARISH":
                ts.direction = TrendDirection.DOWNTREND
                ts.state = TrendState.VALID
            else:
                ts.direction = TrendDirection.SIDEWAYS
                # If they disagree or any is invalid/mixed, the structural state of the trend is INVALID
                ts.state = TrendState.INVALID

        return TrendStageResult(
            stage_name=self.name,
            status=TrendStageStatus.SUCCESS,
            duration_ms=(time.time() - start_time) * 1000
        )
