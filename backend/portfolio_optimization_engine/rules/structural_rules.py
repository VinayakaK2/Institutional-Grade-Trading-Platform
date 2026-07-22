from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext

class PortfolioOptimizationStructuralRules:
    """
    Validates structural presence of all required artifacts.
    """
    def validate(self, context: PortfolioOptimizationExecutionContext) -> None:
        if not context.portfolio_state_snapshot:
            raise ValueError("Missing PortfolioStateSnapshot")
        if not context.portfolio_exposure_snapshot:
            raise ValueError("Missing PortfolioExposureSnapshot")
        if not context.portfolio_correlation_snapshot:
            raise ValueError("Missing PortfolioCorrelationSnapshot")
        if not context.portfolio_decision_snapshot:
            raise ValueError("Missing PortfolioDecisionSnapshot")
        if not context.configuration:
            raise ValueError("Missing PortfolioOptimizationConfiguration")
        if not context.dataset_version:
            raise ValueError("Missing dataset_version")
