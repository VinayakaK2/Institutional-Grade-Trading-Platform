from typing import List, Dict, Type
from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import DecisionEvidenceBase

class RiskDecisionPipeline:
    """
    Executes a linear sequence of decision stages.
    """
    def __init__(self, stages: List[IRiskDecisionStage]):
        self._stages = stages
        
    async def run(self, context: RiskDecisionContext) -> Dict[Type[IRiskDecisionStage], DecisionEvidenceBase]:
        results = {}
        for stage in self._stages:
            evidence = await stage.evaluate(context)
            results[type(stage)] = evidence
            
            if context.configuration.fail_fast and evidence.status == "FAIL":
                # For Risk Decision, fail_fast might not be ideal since we want all reasons, 
                # but if configured, we respect it. Usually we'd evaluate all.
                break
                
        return results
