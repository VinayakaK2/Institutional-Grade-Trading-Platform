"""
Price Structure Detection Stage
===============================

Retrieves Market Structure Points and detects the structural alignment.
"""
import time
from backend.trend_engine.contracts.contracts import ITrendStage, IStructureProvider
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.models.models import TrendStageResult, TrendStageStatus
from backend.market_structure_engine.models.structure import StructureType

class PriceStructureDetectionStage(ITrendStage):
    """
    Evaluates Higher High / Higher Low and Lower High / Lower Low patterns.
    """
    
    def __init__(self, provider: IStructureProvider):
        self._provider = provider
        
    @property
    def name(self) -> str:
        return "PriceStructureDetection"

    async def execute(self, context: TrendExecutionContext) -> TrendStageResult:
        start_time = time.time()
        warnings = []
        
        structure_snapshot_id = context.source_structure_snapshot_id
        if not structure_snapshot_id:
            return TrendStageResult(
                stage_name=self.name,
                status=TrendStageStatus.FAILED,
                duration_ms=(time.time() - start_time) * 1000,
                warnings=["Missing source_structure_snapshot_id in context."]
            )

        for ts in context.symbols:
            try:
                # Limit 2 gets the two most recent structure points
                structures = await self._provider.get_latest_structures(
                    symbol=ts.watchlist_symbol.symbol,
                    snapshot_id=structure_snapshot_id,
                    limit=2
                )
                
                if len(structures) < 2:
                    ts.stage_metadata["structure_alignment"] = "UNKNOWN"
                    ts.stage_metadata["structure_error"] = "Not enough structure points available"
                    continue
                
                # Check for HH/HL or LH/LL
                # Note: structures are returned ordered by time descending (most recent first)
                s1, s2 = structures[0], structures[1]
                types = {s1.type, s2.type}
                
                if types == {StructureType.HH, StructureType.HL}:
                    ts.stage_metadata["structure_alignment"] = "BULLISH"
                elif types == {StructureType.LH, StructureType.LL}:
                    ts.stage_metadata["structure_alignment"] = "BEARISH"
                else:
                    ts.stage_metadata["structure_alignment"] = "MIXED"
                    
            except Exception as e:
                ts.stage_metadata["structure_alignment"] = "UNKNOWN"
                ts.stage_metadata["structure_error"] = str(e)
                warnings.append(f"Error processing {ts.watchlist_symbol.symbol.symbol}: {e}")

        return TrendStageResult(
            stage_name=self.name,
            status=TrendStageStatus.SUCCESS,
            duration_ms=(time.time() - start_time) * 1000,
            warnings=warnings
        )
