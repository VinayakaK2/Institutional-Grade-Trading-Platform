from backend.shared.snapshots.models import BaseSnapshot
from backend.portfolio_decision_engine.models.decision_models import PortfolioDecision
from backend.portfolio_decision_engine.models.references import PortfolioDecisionLineage

class PortfolioDecisionSnapshot(BaseSnapshot):
    """
    The canonical immutable entity resulting from the portfolio decision pipeline execution.
    Contains the final decision, structured reasons, infrastructure metadata, lineage, and the hash.
    """
    decision: PortfolioDecision
    lineage: PortfolioDecisionLineage
    configuration_snapshot_id: str
    business_fingerprint: str
    
    model_config = {"frozen": True}
