from backend.liquidity_grab_engine.lifecycle.contracts.aggregator import ILifecycleAggregator
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LifecycleEvidence, 
    LifecycleSummary, 
    LiquidityGrabLifecycleState
)

class DefaultLifecycleAggregator(ILifecycleAggregator):
    def aggregate(self, evidence: LifecycleEvidence) -> LifecycleSummary:
        """
        Applies deterministic precedence: FAILED > EXPIRED > WEAKENING > CONTINUING > ACTIVE
        and sets decision_reason for debugging purposes.
        """
        if evidence.failure_evidence and evidence.failure_evidence.is_failed:
            return LifecycleSummary(
                state=LiquidityGrabLifecycleState.FAILED,
                aggregator_version="1.0.0",
                decision_reason=evidence.failure_evidence.reason or "Failure conditions met"
            )
            
        if evidence.expiration_evidence and evidence.expiration_evidence.is_expired:
            return LifecycleSummary(
                state=LiquidityGrabLifecycleState.EXPIRED,
                aggregator_version="1.0.0",
                decision_reason=evidence.expiration_evidence.reason or "Candidate expired"
            )
            
        if evidence.weakening_evidence and evidence.weakening_evidence.is_weakening:
            return LifecycleSummary(
                state=LiquidityGrabLifecycleState.WEAKENING,
                aggregator_version="1.0.0",
                decision_reason=evidence.weakening_evidence.reason or "Weakening evidence detected"
            )
            
        if evidence.continuation_evidence and evidence.continuation_evidence.is_continuing:
            return LifecycleSummary(
                state=LiquidityGrabLifecycleState.CONTINUING,
                aggregator_version="1.0.0",
                decision_reason=evidence.continuation_evidence.reason or "Continuation evidence detected"
            )
            
        return LifecycleSummary(
            state=LiquidityGrabLifecycleState.ACTIVE,
            aggregator_version="1.0.0",
            decision_reason="Default active state"
        )
