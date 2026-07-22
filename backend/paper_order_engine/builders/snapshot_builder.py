import hashlib
import json
import uuid
from datetime import datetime, timezone
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext
from backend.paper_order_engine.utils.pipeline_version import PIPELINE_VERSION
from backend.paper_order_engine.utils.snapshot_version import SnapshotVersionProvider

class PaperOrderSnapshotBuilder:
    """
    Responsible for building the immutable PaperOrderSnapshot.
    """
    def build(self, execution_context: PaperOrderExecutionContext, pipeline_context: PaperOrderPipelineContext) -> PaperOrderSnapshot:
        # Deterministic inputs that define the business fingerprint
        # Crucially, we exclude timestamps, durations, and diagnostic traces
        business_components = {
            "symbol": execution_context.symbol,
            "timeframe": execution_context.timeframe,
            "dataset_version": execution_context.dataset_version,
            "parent_portfolio_decision_snapshot_version": execution_context.parent_portfolio_decision_snapshot_version,
            "parent_paper_execution_snapshot_version": execution_context.parent_paper_execution_snapshot_version,
            "configuration": execution_context.configuration,
            "pipeline_version": PIPELINE_VERSION,
            "order_state": pipeline_context.intermediate_order_state.value
        }
        
        # Canonical JSON encoding: dict keys sorted, utf-8
        business_encoded = json.dumps(business_components, sort_keys=True).encode('utf-8')
        business_fingerprint = hashlib.sha256(business_encoded).hexdigest()

        # The actual creation time and UUID for the physical snapshot wrapper
        snapshot_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        schema_version = "1.0.0"
        
        snapshot_version = SnapshotVersionProvider.generate(schema_version, business_fingerprint)

        # Full state capture (Canonical Hash)
        full_components = {
            "snapshot_id": snapshot_id,
            "snapshot_version": snapshot_version,
            "business_fingerprint": business_fingerprint,
            "metadata": execution_context.metadata,
            "diagnostics": pipeline_context.diagnostics.model_dump(),
            "telemetry": pipeline_context.telemetry.model_dump(),
            "created_at": created_at.isoformat()
        }
        
        # Canonical hash
        full_encoded = json.dumps(full_components, sort_keys=True).encode('utf-8')
        snapshot_hash = hashlib.sha256(full_encoded).hexdigest()

        return PaperOrderSnapshot(
            snapshot_id=snapshot_id,
            schema_version=schema_version,
            snapshot_version=snapshot_version,
            parent_portfolio_decision_snapshot_version=execution_context.parent_portfolio_decision_snapshot_version,
            parent_paper_execution_snapshot_version=execution_context.parent_paper_execution_snapshot_version,
            order_state=pipeline_context.intermediate_order_state,
            order_metadata=execution_context.metadata,
            business_fingerprint=business_fingerprint,
            snapshot_hash=snapshot_hash,
            created_at=created_at,
            dataset_version=execution_context.dataset_version,
            metadata=execution_context.metadata
        )
