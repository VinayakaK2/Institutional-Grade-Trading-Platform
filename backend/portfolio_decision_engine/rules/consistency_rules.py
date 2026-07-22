from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionExecutionContext

class PortfolioDecisionConsistencyRules:
    """
    Validates cross-snapshot dataset and fingerprint compatibility to prevent data cross-contamination.
    """
    def validate(self, context: PortfolioDecisionExecutionContext) -> None:
        # Check Business Fingerprints match (crucial to ensure we are evaluating the SAME trade intent)
        fp_state = context.portfolio_state_snapshot.parent_snapshot_references.portfolio_fingerprint
        fp_exposure = context.portfolio_exposure_snapshot.parent_snapshot_references.portfolio_fingerprint
        fp_correlation = getattr(context.portfolio_correlation_snapshot, 'business_fingerprint', fp_state)
        fp_risk = getattr(context.risk_decision_snapshot, 'business_fingerprint', fp_state)
        fp_candidate = context.candidate_position_snapshot.business_fingerprint
        
        fingerprints = {
            "portfolio_state": fp_state,
            "portfolio_exposure": fp_exposure,
            "portfolio_correlation": fp_correlation,
            "risk_decision": fp_risk,
            "candidate_position": fp_candidate
        }

        fp_values = list(fingerprints.values())
        if len(set(fp_values)) > 1:
            raise ValueError(f"Business fingerprint mismatch across upstream snapshots: {fingerprints}")

        # Check dataset versions match for portfolio-wide elements
        ds_state = context.portfolio_state_snapshot.dataset_version
        ds_exposure = context.portfolio_exposure_snapshot.dataset_version
        
        corr_refs = context.portfolio_correlation_snapshot.parent_snapshot_references
        ds_correlation = getattr(corr_refs, 'dataset_version', ds_state)
        ds_candidate = context.candidate_position_snapshot.dataset_version

        dataset_versions = {
            "portfolio_state": ds_state,
            "portfolio_exposure": ds_exposure,
            "portfolio_correlation": ds_correlation,
            "candidate_position": ds_candidate
        }

        # Handle None edge case gracefully
        ds_values = [v for v in dataset_versions.values() if v is not None]
        if ds_values and len(set(ds_values)) > 1:
            raise ValueError(f"Dataset version mismatch across upstream snapshots: {dataset_versions}")
