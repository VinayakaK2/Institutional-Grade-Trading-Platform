import hashlib
import json
from datetime import datetime, timezone
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.models.snapshot import RiskSnapshot, PipelineResult, ValidationResult, RiskMetadata

class RiskSnapshotBuilder:
    """
    Pure builder for RiskSnapshot.
    No repository queries, no I/O, no logging.
    Strictly assembles and fingerprints the final immutable state.
    """
    
    @staticmethod
    def _generate_deterministic_id(
        context: RiskExecutionContext,
        pipeline_result: PipelineResult,
        validation_status: ValidationResult,
        metadata: RiskMetadata
    ) -> str:
        """
        Creates a deterministic SHA-256 ID based on the snapshot components.
        """
        payload = {
            "context": context.model_dump(mode='json'),
            "pipeline_result": pipeline_result.model_dump(mode='json'),
            "validation_status": validation_status.model_dump(mode='json'),
            "metadata": metadata.model_dump(mode='json')
        }
        
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
    @staticmethod
    def build(
        context: RiskExecutionContext,
        pipeline_result: PipelineResult,
        validation_status: ValidationResult,
        metadata: RiskMetadata
    ) -> RiskSnapshot:
        """
        Constructs the final RiskSnapshot.
        """
        snapshot_id = RiskSnapshotBuilder._generate_deterministic_id(
            context, pipeline_result, validation_status, metadata
        )
        
        return RiskSnapshot(
            snapshot_id=snapshot_id,
            context=context,
            pipeline_result=pipeline_result,
            validation_status=validation_status,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
