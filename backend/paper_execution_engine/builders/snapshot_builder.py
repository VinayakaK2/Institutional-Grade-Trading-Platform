import hashlib
import uuid
import json
from datetime import datetime
from backend.paper_execution_engine.models.contexts import PaperExecutionContext, PaperExecutionPipelineContext
from backend.paper_execution_engine.models.snapshot import PaperExecutionSnapshot

class PaperExecutionSnapshotBuilder:
    """
    Responsible for constructing the immutable snapshot, generating the
    deterministic business fingerprint, and managing lineage mappings.
    """
    
    def build(self, execution_context: PaperExecutionContext, pipeline_context: PaperExecutionPipelineContext) -> PaperExecutionSnapshot:
        
        fingerprint = self._generate_fingerprint(execution_context)
        
        # Snapshot hash includes everything to uniquely identify this snapshot physically.
        snapshot_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        schema_version = "1.0.0"
        
        # Creating a unique snapshot hash
        hash_components = {
            "snapshot_id": snapshot_id,
            "created_at": created_at.isoformat(),
            "fingerprint": fingerprint,
            "pipeline_metrics": pipeline_context.pipeline_metrics
        }
        
        snapshot_hash = hashlib.sha256(
            json.dumps(hash_components, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        snapshot_version = f"v_{schema_version}_{fingerprint[:8]}"
        
        return PaperExecutionSnapshot(
            snapshot_id=snapshot_id,
            snapshot_version=snapshot_version,
            schema_version=schema_version,
            dataset_version=execution_context.dataset_version,
            created_at=created_at,
            business_fingerprint=fingerprint,
            engine_version=execution_context.configuration.engine_version,
            pipeline_version=execution_context.configuration.pipeline_version,
            configuration_hash=self._generate_config_hash(execution_context),
            snapshot_hash=snapshot_hash,
            parent_snapshot_versions=[execution_context.parent_portfolio_decision_snapshot_version]
        )
        
    def _generate_fingerprint(self, context: PaperExecutionContext) -> str:
        """
        Generates a deterministic business fingerprint. 
        MUST depend ONLY on deterministic business inputs.
        NEVER include timestamps, runtime, memory, execution duration, UUIDs, or repository ids.
        """
        fingerprint_components = {
            "configuration": context.configuration.model_dump(),
            "dataset_version": context.dataset_version,
            "symbol": context.symbol,
            "timeframe": context.timeframe,
            "parent_snapshot_versions": [context.parent_portfolio_decision_snapshot_version],
            "pipeline_version": context.configuration.pipeline_version
        }
        
        return hashlib.sha256(
            json.dumps(fingerprint_components, sort_keys=True).encode('utf-8')
        ).hexdigest()

    def _generate_config_hash(self, context: PaperExecutionContext) -> str:
        return hashlib.sha256(
            json.dumps(context.configuration.model_dump(), sort_keys=True).encode('utf-8')
        ).hexdigest()
