import hashlib
import json
from datetime import datetime, timezone
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.report import PositionSizingReport
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot, PositionSizingMetadata

class PositionSizingSnapshotBuilder:
    """
    Pure builder for PositionSizingSnapshot.
    """
    
    @staticmethod
    def _generate_deterministic_id(
        context: PositionSizingContext,
        report: PositionSizingReport
    ) -> str:
        # Excludes metadata (execution_duration_ms, logs, etc) to ensure pure determinism
        report_dict = report.model_dump(mode='json')
        
        # Strip timestamps from evidence objects to ensure pure determinism across time
        for key, value in report_dict.items():
            if isinstance(value, dict) and "timestamp" in value:
                del value["timestamp"]
                
        payload = {
            "snapshot_schema_version": "1.0.0",
            "context": context.model_dump(mode='json'),
            "report": report_dict
        }
        
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
    @staticmethod
    def build(
        context: PositionSizingContext,
        report: PositionSizingReport,
        metadata: PositionSizingMetadata
    ) -> PositionSizingSnapshot:
        
        snapshot_id = PositionSizingSnapshotBuilder._generate_deterministic_id(
            context, report
        )
        
        return PositionSizingSnapshot(
            snapshot_id=snapshot_id,
            context=context,
            report=report,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
