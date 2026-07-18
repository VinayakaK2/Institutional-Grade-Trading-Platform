import time
from typing import Dict, Any

from backend.trade_validation_engine.signal_aggregation.stages.base import IAggregationStage
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult, AggregatedTradeEvidence
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import EvidenceAssemblyError

class EvidenceAssemblyStage(IAggregationStage):
    """
    Final stage of the pipeline. Pulls evidence from pipeline state (populated by prior stages)
    and constructs the final AggregatedTradeEvidence object.
    """
    @property
    def stage_id(self) -> str:
        return "EvidenceAssemblyStage"

    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        start_time = time.monotonic()
        try:
            # We expect the prior stages to have stored their evidence in pipeline_state
            # by stage_id
            
            universe_result = pipeline_state.get("UniverseAggregationStage")
            watchlist_result = pipeline_state.get("WatchlistAggregationStage")
            trend_result = pipeline_state.get("TrendAggregationStage")
            consolidation_result = pipeline_state.get("ConsolidationAggregationStage")
            liquidity_grab_result = pipeline_state.get("LiquidityGrabAggregationStage")
            
            missing = []
            if not universe_result or not universe_result.success:
                missing.append("Universe")
            if not watchlist_result or not watchlist_result.success:
                missing.append("Watchlist")
            if not trend_result or not trend_result.success:
                missing.append("Trend")
            if not consolidation_result or not consolidation_result.success:
                missing.append("Consolidation")
            if not liquidity_grab_result or not liquidity_grab_result.success:
                missing.append("LiquidityGrab")
            
            if missing:
                raise EvidenceAssemblyError(f"Cannot assemble evidence. Missing or failed dependencies: {', '.join(missing)}")
                
            config_hash = hash(str(request.configuration.model_dump()))
            # Ensure config_hash is positive and short, or just use string hash
            config_hash_str = str(abs(config_hash))

            assembled_evidence = AggregatedTradeEvidence(
                symbol=request.symbol,
                timeframe=request.timeframe,
                dataset_version=request.dataset_version,
                universe_evidence=universe_result.evidence,
                watchlist_evidence=watchlist_result.evidence,
                trend_evidence=trend_result.evidence,
                consolidation_evidence=consolidation_result.evidence,
                liquidity_grab_evidence=liquidity_grab_result.evidence,
                configuration_hash=config_hash_str,
                metadata={}
            )

            duration = int((time.monotonic() - start_time) * 1000)
            return AggregationStageResult(
                stage_id=self.stage_id,
                success=True,
                evidence=assembled_evidence,
                duration_ms=duration
            )

        except Exception as e:
            duration = int((time.monotonic() - start_time) * 1000)
            return AggregationStageResult(
                stage_id=self.stage_id,
                success=False,
                error_message=str(e),
                duration_ms=duration
            )
