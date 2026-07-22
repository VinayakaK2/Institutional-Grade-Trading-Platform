from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionExecutionContext

class PortfolioDecisionStructuralRules:
    """
    Validates the structural integrity of the input context.
    Ensures all necessary snapshots are present and well-formed.
    """
    def validate(self, context: PortfolioDecisionExecutionContext) -> None:
        if not context.portfolio_state_snapshot:
            raise ValueError("Portfolio State Snapshot is missing.")
        if not context.portfolio_exposure_snapshot:
            raise ValueError("Portfolio Exposure Snapshot is missing.")
        if not context.portfolio_correlation_snapshot:
            raise ValueError("Portfolio Correlation Snapshot is missing.")
        if not context.risk_decision_snapshot:
            raise ValueError("Risk Decision Snapshot is missing.")
        if not context.candidate_position_snapshot:
            raise ValueError("Candidate Position Snapshot is missing.")
        if not context.configuration:
            raise ValueError("Configuration Snapshot is missing.")
