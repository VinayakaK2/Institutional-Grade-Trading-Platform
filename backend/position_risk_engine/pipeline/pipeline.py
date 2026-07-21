from typing import List, Dict
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import RiskEvidenceBase
from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage

class PositionRiskPipeline:
    """
    Executes all risk metric stages.
    Returns a dictionary mapping stage names to evidence objects.
    """
    def __init__(self, stages: List[IRiskMetricStage] = None):
        self._stages = stages or []
        
    def register_stage(self, stage: IRiskMetricStage) -> None:
        self._stages.append(stage)
        
    async def execute(self, context: PositionRiskEvaluationContext) -> Dict[str, RiskEvidenceBase]:
        results: Dict[str, RiskEvidenceBase] = {}
        
        for stage in self._stages:
            try:
                evidence = await stage.calculate(context)
                results[stage.stage_name] = evidence
            except Exception as e:
                if context.configuration.fail_fast:
                    raise e
                    
        return results
