import hashlib
import json
from datetime import datetime, timezone
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import RiskEvaluationReport
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot, PositionRiskMetadata

class RiskEvaluationSnapshotBuilder:
    """
    Pure builder for RiskEvaluationSnapshot.
    """
    
    @staticmethod
    def _generate_deterministic_id(
        context: PositionRiskEvaluationContext,
        report: RiskEvaluationReport,
        metadata: PositionRiskMetadata
    ) -> str:
        payload = {
            "context": context.model_dump(mode='json'),
            "report": report.model_dump(mode='json'),
            "metadata": metadata.model_dump(mode='json')
        }
        
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
    @staticmethod
    def build(
        context: PositionRiskEvaluationContext,
        report: RiskEvaluationReport,
        metadata: PositionRiskMetadata
    ) -> RiskEvaluationSnapshot:
        
        snapshot_id = RiskEvaluationSnapshotBuilder._generate_deterministic_id(
            context, report, metadata
        )
        
        return RiskEvaluationSnapshot(
            snapshot_id=snapshot_id,
            context=context,
            report=report,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
