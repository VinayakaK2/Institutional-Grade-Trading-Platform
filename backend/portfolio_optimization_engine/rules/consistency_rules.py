from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext

class PortfolioOptimizationConsistencyRules:
    """
    Validates semantic consistency across the snapshot graph.
    """
    def validate(self, context: PortfolioOptimizationExecutionContext) -> None:
        dataset_version = context.dataset_version

        # 1. Dataset Version Alignment
        ds_state = getattr(context.portfolio_state_snapshot, "dataset_version", None)
        ds_exposure = getattr(context.portfolio_exposure_snapshot, "dataset_version", None)
        
        if ds_state and ds_state != dataset_version:
            raise ValueError(f"Dataset version mismatch in PortfolioStateSnapshot. Expected {dataset_version}, got {ds_state}")
        
        if ds_exposure and ds_exposure != dataset_version:
            raise ValueError(f"Dataset version mismatch in PortfolioExposureSnapshot. Expected {dataset_version}, got {ds_exposure}")

        # 2. Lineage / Parent References Validation
        # The PortfolioDecisionSnapshot must descend from the same exact snapshots provided in the context
        try:
            decision_lineage = context.portfolio_decision_snapshot.lineage
        except AttributeError:
            # If the decision snapshot lacks lineage, we fail validation
            raise ValueError("PortfolioDecisionSnapshot is missing lineage details")
            
        if decision_lineage.portfolio_state_snapshot.snapshot_id != context.portfolio_state_snapshot.snapshot_id:
            raise ValueError("Lineage mismatch: PortfolioDecisionSnapshot state parent does not match context state snapshot")
            
        if decision_lineage.portfolio_exposure_snapshot.snapshot_id != context.portfolio_exposure_snapshot.snapshot_id:
            raise ValueError("Lineage mismatch: PortfolioDecisionSnapshot exposure parent does not match context exposure snapshot")
            
        if decision_lineage.portfolio_correlation_snapshot.snapshot_id != context.portfolio_correlation_snapshot.snapshot_id:
            raise ValueError("Lineage mismatch: PortfolioDecisionSnapshot correlation parent does not match context correlation snapshot")

        # 3. Configuration Hash presence
        if not context.configuration.configuration_hash:
            raise ValueError("Invalid configuration hash")
