import hashlib
import json
import uuid
from datetime import datetime, timezone
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext
from backend.paper_fill_engine.utils.pipeline_version import PIPELINE_VERSION
from backend.paper_fill_engine.utils.snapshot_version import SnapshotVersionProvider

class PaperFillSnapshotBuilder:
    """
    Responsible for building the immutable PaperFillSnapshot.
    """
    def build(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext) -> PaperFillSnapshot:
        sim_res = pipeline_context.simulation_result
        
        if sim_res:
            fill_events = sorted(sim_res.fill_events, key=lambda e: e.sequence_number)
            
            # Defensive check
            if sum(e.quantity for e in fill_events) != sim_res.total_filled_quantity:
                raise ValueError("Defensive check failed: Sum of event quantities does not match total_filled_quantity")
                
            # Exclude random fill_ids from business fingerprint to maintain deterministic replay
            event_dicts = []
            for e in fill_events:
                d = e.model_dump()
                d.pop("fill_id", None)
                event_dicts.append(d)
        else:
            event_dicts = []

        # Business fingerprint excludes execution time, diagnostics, telemetry, runtime IDs
        business_components = {
            "symbol": execution_context.symbol,
            "timeframe": execution_context.timeframe,
            "dataset_version": execution_context.dataset_version,
            "parent_paper_order_snapshot_version": execution_context.parent_paper_order_snapshot_version,
            "configuration": execution_context.configuration,
            "pipeline_version": PIPELINE_VERSION,
            "fill_state": sim_res.fill_state.value if sim_res else None,
            "fill_events": event_dicts,
            "total_filled_quantity": sim_res.total_filled_quantity if sim_res else 0,
            "remaining_quantity": sim_res.remaining_quantity if sim_res else 0,
            "average_fill_price": sim_res.average_fill_price if sim_res else None,
        }
        
        business_encoded = json.dumps(business_components, sort_keys=True).encode('utf-8')
        business_fingerprint = hashlib.sha256(business_encoded).hexdigest()

        snapshot_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        schema_version = "1.0.0"
        
        snapshot_version = SnapshotVersionProvider.generate(schema_version, business_fingerprint)

        # Full state capture (Canonical Hash) includes runtime and diagnostic data
        full_components = {
            "snapshot_id": snapshot_id,
            "snapshot_version": snapshot_version,
            "business_fingerprint": business_fingerprint,
            "metadata": execution_context.metadata,
            "diagnostics": pipeline_context.diagnostics.model_dump(),
            "telemetry": pipeline_context.telemetry.model_dump(),
            "created_at": created_at.isoformat()
        }
        
        full_encoded = json.dumps(full_components, sort_keys=True).encode('utf-8')
        snapshot_hash = hashlib.sha256(full_encoded).hexdigest()

        return PaperFillSnapshot(
            snapshot_id=snapshot_id,
            schema_version=schema_version,
            snapshot_version=snapshot_version,
            parent_paper_order_snapshot_version=execution_context.parent_paper_order_snapshot_version,
            fill_state=pipeline_context.simulation_result.fill_state if pipeline_context.simulation_result else FillState.PENDING_FILL,
            fill_events=pipeline_context.simulation_result.fill_events if pipeline_context.simulation_result else [],
            total_filled_quantity=pipeline_context.simulation_result.total_filled_quantity if pipeline_context.simulation_result else 0,
            remaining_quantity=pipeline_context.simulation_result.remaining_quantity if pipeline_context.simulation_result else 0,
            average_fill_price=pipeline_context.simulation_result.average_fill_price if pipeline_context.simulation_result else None,
            business_fingerprint=business_fingerprint,
            snapshot_hash=snapshot_hash,
            created_at=created_at,
            dataset_version=execution_context.dataset_version,
            metadata=execution_context.metadata
        )
