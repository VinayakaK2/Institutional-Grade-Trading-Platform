import json
import hashlib
from datetime import datetime, timezone
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.report import PortfolioRiskReport
from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot, PortfolioRiskMetadata

class PortfolioRiskSnapshotBuilder:
    """
    Constructs PortfolioRiskSnapshots and generates deterministic SHA-256 IDs.
    """
    
    @staticmethod
    def _generate_deterministic_id(
        context: PortfolioRiskContext,
        report: PortfolioRiskReport
    ) -> str:
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
        context: PortfolioRiskContext,
        report: PortfolioRiskReport,
        execution_duration_ms: int
    ) -> PortfolioRiskSnapshot:
        
        snapshot_id = PortfolioRiskSnapshotBuilder._generate_deterministic_id(context, report)
        
        metadata = PortfolioRiskMetadata(
            execution_duration_ms=execution_duration_ms,
            additional_info={"pipeline_version": context.configuration.pipeline_version}
        )
        
        return PortfolioRiskSnapshot(
            snapshot_id=snapshot_id,
            context=context,
            report=report,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
