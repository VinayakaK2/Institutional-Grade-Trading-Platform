from typing import Dict, Type
from datetime import datetime, timezone
from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.evidence import (
    DecisionEvidenceBase, FinalDecisionEvidence, DecisionExplanation,
    DecisionType, StageStatus
)

class DecisionResolver:
    """
    Evaluates all evidence from the pipeline and computes the final deterministic decision.
    """
    def resolve(self, evidence_map: Dict[Type[IRiskDecisionStage], DecisionEvidenceBase], snapshot_id: str, algorithm_version: str) -> FinalDecisionEvidence:
        failed_stages = []
        
        for stage_type, evidence in evidence_map.items():
            if evidence.status == StageStatus.FAIL:
                failed_stages.append(stage_type.__name__)
                
        if not failed_stages:
            decision = DecisionType.APPROVED
            primary_reason = "All risk and portfolio constraints passed."
        else:
            # We strictly REJECT if any stage fails in this model.
            decision = DecisionType.REJECTED
            primary_reason = f"Failed constraints in stages: {', '.join(failed_stages)}"
            
        explanation = DecisionExplanation(
            decision=decision,
            primary_reason=primary_reason,
            contributing_evidence=[ev.metric_id for ev in evidence_map.values() if ev.status == StageStatus.FAIL]
        )
        
        return FinalDecisionEvidence(
            metric_id=f"final_dec_{snapshot_id}",
            decision=decision,
            reason=explanation,
            triggered_rules=failed_stages,
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm_version=algorithm_version
        )
