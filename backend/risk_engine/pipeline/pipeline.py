import time
from typing import List, Dict, Any
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.models.snapshot import PipelineResult
from backend.risk_engine.pipeline.contracts import IRiskPipelineStage

class RiskPipeline:
    """
    Reusable pipeline infrastructure for the Risk Engine.
    Executes ordered stages, propagates immutable context, supports fail-fast.
    """
    def __init__(self, stages: List[IRiskPipelineStage] = None):
        self._stages = stages or []
        
    def register_stage(self, stage: IRiskPipelineStage) -> None:
        """Dynamically register a stage."""
        self._stages.append(stage)
        
    async def execute(self, context: RiskExecutionContext) -> PipelineResult:
        """
        Coordinates execution of all registered stages sequentially.
        Even with zero stages, it returns success.
        """
        stage_results: Dict[str, Any] = {}
        
        for stage in self._stages:
            start_t = time.time()
            try:
                result = await stage.execute(context)
                duration = int((time.time() - start_t) * 1000)
                
                stage_results[stage.stage_name] = {
                    "status": "PASS",
                    "duration_ms": duration,
                    "payload": result
                }
            except Exception as e:
                duration = int((time.time() - start_t) * 1000)
                stage_results[stage.stage_name] = {
                    "status": "FAIL",
                    "duration_ms": duration,
                    "error": str(e)
                }
                
                if context.configuration.fail_fast:
                    return PipelineResult(success=False, stage_results=stage_results)
                    
        return PipelineResult(success=True, stage_results=stage_results)
