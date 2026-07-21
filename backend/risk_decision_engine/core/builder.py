import hashlib
import json
from typing import Any
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import DecisionType

class RiskDecisionSnapshotBuilder:
    """
    Constructs deterministic, immutable snapshots of risk decisions.
    """
    
    @classmethod
    def _hash_dict(cls, data: Any) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
        
    @classmethod
    def generate_snapshot_id(
        cls,
        context: RiskDecisionContext,
        algorithm_version: str,
        decision: DecisionType
    ) -> str:
        """
        Generates a purely deterministic canonical ID based on configuration, lineage, and final decision.
        Timestamps are strictly excluded.
        """
        canonical_state = {
            "risk_snapshot_id": context.parent_snapshots.risk_snapshot_id,
            "sizing_snapshot_id": context.parent_snapshots.sizing_snapshot_id,
            "portfolio_snapshot_id": context.parent_snapshots.portfolio_snapshot_id,
            "dataset_version": context.parent_snapshots.dataset_version,
            "configuration": context.configuration.model_dump(),
            "algorithm_version": algorithm_version,
            "decision": decision.value
        }
        
        return cls._hash_dict(canonical_state)
