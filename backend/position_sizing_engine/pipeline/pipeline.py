from typing import List, Dict
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage

class PositionSizingPipeline:
    """
    Executes all sizing metric stages sequentially.
    Passes results of previous stages forward to support evidence-driven pipelines.
    """
    def __init__(self, stages: List[ISizingMetricStage] = None):
        self._stages = stages or []
        
    def register_stage(self, stage: ISizingMetricStage) -> None:
        self._stages.append(stage)
        
    async def execute(self, context: PositionSizingContext) -> Dict[str, SizingEvidenceBase]:
        results: Dict[str, SizingEvidenceBase] = {}
        
        for stage in self._stages:
            try:
                evidence = await stage.calculate(context, results)
                results[stage.stage_name] = evidence
            except Exception as e:
                if context.configuration.fail_fast:
                    raise e
                    
        return results
