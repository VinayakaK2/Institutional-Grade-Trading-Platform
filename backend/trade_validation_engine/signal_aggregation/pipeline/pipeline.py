from typing import List, Tuple, Dict, Any

from backend.trade_validation_engine.signal_aggregation.stages.base import IAggregationStage
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult

class SignalAggregationPipeline:
    """
    Executes aggregation stages in order and coordinates pipeline state.
    """
    def __init__(self, stages: List[IAggregationStage]):
        self._stages = stages

    async def execute(self, request: SignalAggregationRequest) -> Tuple[bool, List[AggregationStageResult]]:
        """
        Executes all registered stages.
        Returns (success, list_of_stage_results).
        """
        pipeline_state: Dict[str, Any] = {}
        stage_results: List[AggregationStageResult] = []
        pipeline_success = True

        for stage in self._stages:
            try:
                result = await stage.execute(request, pipeline_state)
            except Exception as e:
                # Catch unexpected stage crashes
                result = AggregationStageResult(
                    stage_id=stage.stage_id,
                    success=False,
                    error_message=f"Unhandled exception during execution: {str(e)}",
                    duration_ms=0
                )
            
            stage_results.append(result)
            pipeline_state[stage.stage_id] = result
            
            if not result.success:
                pipeline_success = False
                if request.configuration.fail_fast:
                    break

        return pipeline_success, stage_results
