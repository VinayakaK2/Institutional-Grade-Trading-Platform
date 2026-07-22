from backend.portfolio_decision_engine.contracts.pipeline import IDecisionStage
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionPipelineContext

class DecisionAggregationStage(IDecisionStage):
    """
    Aggregates immutable facts from upstream snapshots into a centralized dictionary
    for the rules engine. Explicitly avoids inventing derived scores, weights, or optimizations.
    """
    def execute(self, context: PortfolioDecisionPipelineContext) -> PortfolioDecisionPipelineContext:
        state = context.execution_context.portfolio_state_snapshot
        exposure = context.execution_context.portfolio_exposure_snapshot
        correlation = context.execution_context.portfolio_correlation_snapshot
        risk = context.execution_context.risk_decision_snapshot
        candidate = context.execution_context.candidate_position_snapshot

        context.aggregated_facts = {
            "portfolio_state": {
                "active_positions_count": len(state.portfolio_state.active_positions),
                "total_portfolio_value": state.portfolio_state.metrics.total_portfolio_value,
            },
            "portfolio_exposure": {
                "gross_exposure": exposure.exposure_analysis.gross_net_exposure.gross_exposure,
                "net_exposure": exposure.exposure_analysis.gross_net_exposure.net_exposure,
            },
            "portfolio_correlation": {
                "highest_symbol_correlation": max(
                    [float(c.correlation) for c in correlation.correlation_analysis.symbol_correlation.pairwise_correlations]
                ) if correlation.correlation_analysis.symbol_correlation.pairwise_correlations else 0.0,
                "overall_correlation_score": correlation.correlation_metrics.average_correlation,
            },
            "risk_decision": {
                "status": risk.report.final_decision_evidence.decision.value,
                "risk_amount": risk.metadata.additional_info.get("risk_amount", 0.0),
            },
            "candidate_position": {
                "symbol": candidate.symbol,
                "strategy": candidate.strategy_identifier,
                "direction": candidate.direction,
            }
        }
        return context
