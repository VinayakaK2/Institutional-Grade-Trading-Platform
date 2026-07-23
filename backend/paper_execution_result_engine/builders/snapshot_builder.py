from datetime import datetime, timezone
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultPipelineContext
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.utils.snapshot_version import SnapshotVersionProvider
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError

class SnapshotBuilder:
    """
    Constructs the final PaperExecutionSnapshot from pipeline context.
    """
    def build(self, context: PaperExecutionResultPipelineContext) -> PaperExecutionSnapshot:
        if not context.execution_status or not context.execution_summary or not context.execution_timeline:
            raise PaperExecutionResultCalculationError("Incomplete execution result context. All stages must complete before building.")
            
        dataset_version = context.execution_context.dataset_version
        created_at = datetime.now(timezone.utc)
        
        fingerprint = (
            f"{context.execution_context.portfolio_decision_snapshot.business_fingerprint}|"
            f"{context.execution_status.value}|"
            f"{context.execution_summary.filled_quantity}|"
            f"{context.execution_summary.average_fill_price}|"
            f"{context.execution_summary.execution_cost}|"
            f"{dataset_version}"
        )
        
        from hashlib import sha256
        business_fingerprint = sha256(fingerprint.encode('utf-8')).hexdigest()
        
        snapshot_id = f"exec_res_{business_fingerprint}"
        snapshot_version = SnapshotVersionProvider.generate()
        canonical_hash = business_fingerprint # Using fingerprint as hash
        
        meta = context.execution_context.metadata.copy()
        meta["configuration_hash"] = context.execution_context.configuration_hash
        
        return PaperExecutionSnapshot(
            snapshot_id=snapshot_id,
            snapshot_version=snapshot_version,
            schema_version="1.0.0",
            dataset_version=dataset_version,
            created_at=created_at,
            parent_portfolio_decision_snapshot_version=context.execution_context.portfolio_decision_snapshot.snapshot_id,
            parent_order_snapshot_version=context.execution_context.paper_order_snapshot.snapshot_version or "none",
            parent_fill_snapshot_version=context.execution_context.paper_fill_snapshot.snapshot_version or "none",
            parent_execution_quality_snapshot_version=context.execution_context.paper_execution_quality_snapshot.snapshot_version or "none",
            execution_status=context.execution_status,
            execution_summary=context.execution_summary,
            execution_timeline=context.execution_timeline,
            business_fingerprint=business_fingerprint,
            canonical_hash=canonical_hash,
            metadata=meta
        )
