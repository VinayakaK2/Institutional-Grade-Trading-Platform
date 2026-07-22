from typing import List
from backend.portfolio_decision_engine.contracts.pipeline import IDecisionStage
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionPipelineContext
from backend.portfolio_decision_engine.models.decision_models import DecisionStatus, DecisionSeverity, DecisionReason

class DecisionRulesStage(IDecisionStage):
    """
    Applies deterministic logic against the aggregated facts.
    Collects all violations (rather than failing early) to generate comprehensive structured DecisionReasons.
    """
    def execute(self, context: PortfolioDecisionPipelineContext) -> PortfolioDecisionPipelineContext:
        facts = context.aggregated_facts
        limits = context.execution_context.configuration.limits
        
        reasons: List[DecisionReason] = []
        status = DecisionStatus.APPROVED

        # 1. Check Risk Decision Input
        if facts["risk_decision"]["status"] == "REJECTED":
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="UPSTREAM_RISK_REJECTION",
                severity=DecisionSeverity.CRITICAL,
                category="RISK",
                message="Upstream Risk Decision Engine rejected the trade.",
                metadata={"risk_status": facts["risk_decision"]["status"]}
            ))
        elif facts["risk_decision"]["status"] == "REDUCED":
            status = DecisionStatus.REDUCED if status == DecisionStatus.APPROVED else status
            reasons.append(DecisionReason(
                code="UPSTREAM_RISK_REDUCTION",
                severity=DecisionSeverity.HIGH,
                category="RISK",
                message="Upstream Risk Decision Engine reduced the trade size.",
                metadata={"risk_status": facts["risk_decision"]["status"]}
            ))
            
        # 2. Portfolio Exposure Limits
        gross_exposure = facts["portfolio_exposure"]["gross_exposure"]
        max_gross = limits.get("max_gross_exposure", 1.0)
        if gross_exposure > max_gross:
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="PORTFOLIO_GROSS_EXPOSURE_LIMIT",
                severity=DecisionSeverity.CRITICAL,
                category="EXPOSURE",
                message="Gross exposure exceeds configured maximum.",
                metadata={"gross_exposure": gross_exposure, "limit": max_gross}
            ))

        net_exposure = facts["portfolio_exposure"]["net_exposure"]
        max_net = limits.get("max_net_exposure", 0.5)
        if abs(net_exposure) > max_net:
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="PORTFOLIO_NET_EXPOSURE_LIMIT",
                severity=DecisionSeverity.CRITICAL,
                category="EXPOSURE",
                message="Absolute net exposure exceeds configured maximum.",
                metadata={"net_exposure": net_exposure, "limit": max_net}
            ))

        # 3. Portfolio Correlation Limits
        overall_correlation = facts["portfolio_correlation"]["overall_correlation_score"]
        max_correlation = limits.get("max_overall_correlation", 0.8)
        if overall_correlation > max_correlation:
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="PORTFOLIO_CORRELATION_LIMIT",
                severity=DecisionSeverity.HIGH,
                category="CORRELATION",
                message="Overall correlation score exceeds configured maximum.",
                metadata={"correlation": overall_correlation, "limit": max_correlation}
            ))
            
        highest_symbol_corr = facts["portfolio_correlation"]["highest_symbol_correlation"]
        max_symbol_corr = limits.get("max_symbol_correlation", 0.9)
        if highest_symbol_corr > max_symbol_corr:
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="SYMBOL_CORRELATION_LIMIT",
                severity=DecisionSeverity.HIGH,
                category="CORRELATION",
                message="Highest single symbol pairwise correlation exceeds maximum.",
                metadata={"highest_symbol_correlation": highest_symbol_corr, "limit": max_symbol_corr}
            ))
            
        # 4. Position limits
        active_positions = facts["portfolio_state"]["active_positions_count"]
        max_positions = limits.get("max_active_positions", 20)
        if active_positions >= max_positions:
            status = DecisionStatus.REJECTED
            reasons.append(DecisionReason(
                code="MAX_ACTIVE_POSITIONS_LIMIT",
                severity=DecisionSeverity.HIGH,
                category="STATE",
                message="Maximum number of active positions reached.",
                metadata={"active_positions": active_positions, "limit": max_positions}
            ))

        # Default Approval Reason if empty
        if not reasons:
            reasons.append(DecisionReason(
                code="ALL_CHECKS_PASSED",
                severity=DecisionSeverity.LOW,
                category="SYSTEM",
                message="All portfolio constraints and upstream risk checks passed.",
                metadata={}
            ))
            
        from backend.portfolio_decision_engine.models.decision_models import PortfolioDecision, DecisionMetadata
        
        # We don't have decision ID or full metadata here, so we will assign temp values 
        # and finalize them in the SnapshotBuilder where infrastructure values exist.
        metadata = DecisionMetadata(
            decision_id="",
            pipeline_version="",
            configuration_version="",
            engine_version="",
            rule_version="",
            execution_duration_ms=0,
            decision_timestamp=""
        )

        context.decision = PortfolioDecision(
            status=status,
            reasons=reasons,
            metadata=metadata
        )

        return context
