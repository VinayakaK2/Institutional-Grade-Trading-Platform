import hashlib
import json
from datetime import datetime, timezone
import uuid
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationPipelineContext
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot, PortfolioOptimizationMetadata
from backend.portfolio_optimization_engine.models.references import ParentSnapshotReferences
from backend.shared.snapshots.models import SnapshotReference

class PortfolioOptimizationSnapshotBuilder:
    """
    Constructs the canonical, deterministic optimization snapshot.
    """
    
    def build(self, context: PortfolioOptimizationPipelineContext) -> PortfolioOptimizationSnapshot:
        if not context.optimization_result:
            raise ValueError("Cannot build snapshot without an OptimizationResult")
            
        execution_context = context.execution_context
        
        # 1. Build Parent Snapshot References
        parent_references = ParentSnapshotReferences(
            portfolio_state_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_state_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_state_snapshot, 'schema_version', None),
                dataset_version=execution_context.portfolio_state_snapshot.dataset_version,
                business_fingerprint=getattr(execution_context.portfolio_state_snapshot, 'business_fingerprint', None)
            ),
            portfolio_exposure_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_exposure_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_exposure_snapshot, 'schema_version', None),
                dataset_version=execution_context.portfolio_exposure_snapshot.dataset_version,
                business_fingerprint=getattr(execution_context.portfolio_exposure_snapshot, 'business_fingerprint', None)
            ),
            portfolio_correlation_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_correlation_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_correlation_snapshot, 'schema_version', None),
                dataset_version=execution_context.portfolio_correlation_snapshot.dataset_version,
                business_fingerprint=getattr(execution_context.portfolio_correlation_snapshot, 'business_fingerprint', None)
            ),
            portfolio_decision_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_decision_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_decision_snapshot, 'schema_version', None),
                dataset_version=execution_context.portfolio_decision_snapshot.dataset_version,
                business_fingerprint=getattr(execution_context.portfolio_decision_snapshot, 'business_fingerprint', None)
            )
        )
        
        # 2. Build Deterministic Business Fingerprint
        # Excludes all runtime diagnostics, timestamps, and transient metadata
        canonical_payload = {
            "dataset_version": execution_context.dataset_version,
            "configuration_hash": execution_context.configuration.configuration_hash,
            "parent_references": parent_references.model_dump(mode="json"),
            "optimization_result": context.optimization_result.model_dump(mode="json")
        }
        
        fingerprint_hash = hashlib.sha256(
            json.dumps(canonical_payload, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        # 3. Build Final Snapshot
        snapshot = PortfolioOptimizationSnapshot(
            snapshot_id=f"po_snap_{uuid.uuid4()}",
            schema_version="1.0.0",
            dataset_version=execution_context.dataset_version,
            created_at=datetime.now(timezone.utc),
            configuration_snapshot_id=execution_context.configuration.configuration_hash,
            business_fingerprint=fingerprint_hash,
            optimization_result=context.optimization_result,
            parent_snapshot_references=parent_references,
            optimization_metadata=PortfolioOptimizationMetadata(
                execution_id=context.execution_id,
                pipeline_version=execution_context.configuration.pipeline_version,
                configuration_version=execution_context.configuration.configuration_hash,
                engine_version="1.0.0"
            )
        )
        
        return snapshot
