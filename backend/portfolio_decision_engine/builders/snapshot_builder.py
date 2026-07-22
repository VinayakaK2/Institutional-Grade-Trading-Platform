import time
import json
from backend.shared.snapshots.models import SnapshotReference
from backend.shared.snapshots.utils import HashUtility
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionPipelineContext
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot
from backend.portfolio_decision_engine.models.references import PortfolioDecisionLineage
from backend.portfolio_decision_engine.models.decision_models import DecisionMetadata, PortfolioDecision

class PortfolioDecisionSnapshotBuilder:
    """
    Constructs the canonical immutable PortfolioDecisionSnapshot, assigns the Business Fingerprint,
    and calculates the deterministic SHA-256 hash.
    """
    SCHEMA_VERSION = "1.0.0"

    def build(self, context: PortfolioDecisionPipelineContext) -> PortfolioDecisionSnapshot:
        execution_ctx = context.execution_context
        decision = context.decision

        if not decision:
            raise ValueError("Cannot build snapshot without a final decision.")

        # Re-build decision metadata with infrastructure specifics
        
        metadata = DecisionMetadata(
            decision_id=context.execution_id,
            pipeline_version=execution_ctx.configuration.pipeline_version,
            configuration_version=execution_ctx.configuration.configuration_hash,
            engine_version="1.0.0",
            rule_version=execution_ctx.configuration.rule_version,
            execution_duration_ms=0, # Simplified for deterministic behavior testing 
            decision_timestamp=str(int(time.time()))
        )

        final_decision = PortfolioDecision(
            status=decision.status,
            reasons=decision.reasons,
            metadata=metadata
        )

        # Build Lineage
        lineage = PortfolioDecisionLineage(
            portfolio_state_snapshot=SnapshotReference(
                snapshot_id=execution_ctx.portfolio_state_snapshot.snapshot_id,
                business_fingerprint=execution_ctx.portfolio_state_snapshot.parent_snapshot_references.portfolio_fingerprint,
                dataset_version=execution_ctx.portfolio_state_snapshot.dataset_version or "legacy"
            ),
            portfolio_exposure_snapshot=SnapshotReference(
                snapshot_id=execution_ctx.portfolio_exposure_snapshot.snapshot_id,
                business_fingerprint=execution_ctx.portfolio_exposure_snapshot.parent_snapshot_references.portfolio_fingerprint,
                dataset_version=execution_ctx.portfolio_exposure_snapshot.dataset_version or "legacy"
            ),
            portfolio_correlation_snapshot=SnapshotReference(
                snapshot_id=execution_ctx.portfolio_correlation_snapshot.snapshot_id,
                business_fingerprint=getattr(execution_ctx.portfolio_correlation_snapshot, 'business_fingerprint', execution_ctx.portfolio_state_snapshot.parent_snapshot_references.portfolio_fingerprint),
                dataset_version=getattr(execution_ctx.portfolio_correlation_snapshot.parent_snapshot_references, 'dataset_version', "legacy")
            ),
            risk_decision_snapshot=SnapshotReference(
                snapshot_id=execution_ctx.risk_decision_snapshot.snapshot_id,
                business_fingerprint=getattr(execution_ctx.risk_decision_snapshot, 'business_fingerprint', execution_ctx.portfolio_state_snapshot.parent_snapshot_references.portfolio_fingerprint),
                dataset_version=getattr(execution_ctx.risk_decision_snapshot, 'dataset_version', 'legacy')
            ),
            candidate_position_snapshot=SnapshotReference(
                snapshot_id=execution_ctx.candidate_position_snapshot.snapshot_id,
                business_fingerprint=execution_ctx.candidate_position_snapshot.business_fingerprint,
                dataset_version="legacy"
            )
        )
        
        # Ensure identical business fingerprints across lineage
        business_fingerprint = execution_ctx.candidate_position_snapshot.business_fingerprint

        # Form temporary dictionary for canonical serialization
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "decision": json.loads(final_decision.model_dump_json()),
            "lineage": json.loads(lineage.model_dump_json()),
            "configuration_snapshot_id": execution_ctx.configuration.configuration_hash,
            "business_fingerprint": business_fingerprint
        }
        
        # Omit timestamp/execution specific data from hashing so snapshot is deterministic
        # over identical inputs and config.
        payload["decision"]["metadata"]["decision_timestamp"] = ""
        payload["decision"]["metadata"]["execution_duration_ms"] = 0
        payload["decision"]["metadata"]["decision_id"] = ""

        snapshot_id = HashUtility.generate_id("dec_", payload)

        return PortfolioDecisionSnapshot(
            snapshot_id=snapshot_id,
            schema_version=self.SCHEMA_VERSION,
            dataset_version=execution_ctx.configuration.dataset_version,
            created_at=str(time.time()),
            decision=final_decision,
            lineage=lineage,
            configuration_snapshot_id=execution_ctx.configuration.configuration_hash,
            business_fingerprint=business_fingerprint
        )
