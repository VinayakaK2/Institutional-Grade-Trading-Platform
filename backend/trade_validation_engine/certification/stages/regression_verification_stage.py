import time
from typing import Dict, Any
from backend.trade_validation_engine.certification.contracts.stage import ICertificationStage
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import StageResult
from backend.trade_validation_engine.certification.engine.snapshot_hasher import SnapshotHasher

class RegressionVerificationStage(ICertificationStage):
    @property
    def stage_name(self) -> str:
        return "Regression"

    async def execute(self, config: CertificationConfig, context: Dict[str, Any]) -> StageResult:
        start_t = time.time()
        
        golden_dataset = context.get("golden_dataset", [])
        expected_snapshots = context.get("expected_snapshots", [])
        engine = context.get("optimization_engine")
        
        if not engine or not golden_dataset or not expected_snapshots:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={"reason": "Missing golden data or engine"})
            
        # Execute golden dataset
        actual_results = await engine.execute_batch(golden_dataset)
        
        # Verify actual vs expected
        mismatches = 0
        for i in range(len(actual_results)):
            expected = expected_snapshots[i]
            actual = actual_results[i][1]
            
            exp_hash = SnapshotHasher.generate_fingerprint(expected)
            act_hash = SnapshotHasher.generate_fingerprint(actual.model_dump())
            if exp_hash != act_hash:
                mismatches += 1
                
        duration = int((time.time() - start_t) * 1000)
        
        context["evidence"] = {
            "mismatches": mismatches,
            "total_verified": len(actual_results)
        }
        
        if mismatches > 0:
            return StageResult(
                stage_name=self.stage_name,
                status="FAIL",
                duration_ms=duration,
                metrics={"mismatches": mismatches}
            )
            
        return StageResult(
            stage_name=self.stage_name,
            status="PASS",
            duration_ms=duration,
            metrics={"mismatches": 0}
        )
