import platform
import uuid
import sys
from typing import List, Dict, Any
from datetime import datetime, timezone
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import CertificationReport, StageResult, QualityGateStatus
from backend.trade_validation_engine.certification.contracts.stage import ICertificationStage
from backend.trade_validation_engine.certification.contracts.repository import ICertificationRepository

class TradeValidationCertificationEngine:
    """
    Formal certification pipeline for Phase 10.6.
    Orchestrates the read-only execution of all validation stages and compiles the immutable CertificationReport.
    """
    def __init__(
        self,
        config: CertificationConfig,
        repository: ICertificationRepository,
        stages: List[ICertificationStage]
    ):
        self._config = config
        self._repository = repository
        self._stages = stages
        
    async def run_certification(self, quality_gates: QualityGateStatus) -> CertificationReport:
        """
        Executes the formal certification pipeline.
        """
        context: Dict[str, Any] = {}
        stage_results: List[StageResult] = []
        overall_result = "CERTIFIED"
        
        start_time = datetime.now(timezone.utc)
        
        for stage in self._stages:
            try:
                # Dependency or user-config may skip certain stages
                if not getattr(self._config, f"enable_{stage.stage_name.lower()}_verification", True):
                    stage_results.append(
                        StageResult(
                            stage_name=stage.stage_name,
                            status="SKIP",
                            duration_ms=0,
                            metrics={"reason": "Disabled in config"}
                        )
                    )
                    continue

                res = await stage.execute(self._config, context)
                
                # Persist evidence immediately if present in context
                if "evidence" in context and context["evidence"]:
                    evidence_path = await self._repository.save_evidence(stage.stage_name, context["evidence"])
                    # Replace with a new StageResult containing the evidence_path
                    res = StageResult(
                        stage_name=res.stage_name,
                        status=res.status,
                        duration_ms=res.duration_ms,
                        metrics=res.metrics,
                        evidence_path=evidence_path,
                        error_message=res.error_message
                    )
                    context["evidence"] = {} # clear for next stage

                stage_results.append(res)
                
                if res.status == "FAIL":
                    overall_result = "FAILED"
                    if self._config.fail_fast:
                        break
                        
            except Exception as e:
                overall_result = "FAILED"
                stage_results.append(
                    StageResult(
                        stage_name=stage.stage_name,
                        status="FAIL",
                        duration_ms=0,
                        metrics={},
                        error_message=str(e)
                    )
                )
                if self._config.fail_fast:
                    break
        
        end_time = datetime.now(timezone.utc)
        total_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Calculate peak memory if tracking exists in context (gathered from stress/perf stages)
        peak_memory = context.get("peak_memory_mb", 0.0)
        snapshot_count = context.get("snapshot_count", 0)
        
        report = CertificationReport(
            certification_id=uuid.uuid4().hex,
            platform_info=f"{platform.system()} {platform.release()} ({platform.machine()})",
            python_version=sys.version,
            git_commit="N/A",  # Could be pulled from env
            dataset_version=self._config.dataset_version,
            dataset_seed=self._config.dataset_seed,
            configuration_hash="dynamic_config", # placeholder for now
            business_fingerprint_version="1.0.0",
            snapshot_count=snapshot_count,
            parallel_workers=self._config.parallel_workers,
            total_execution_time_ms=total_time_ms,
            peak_memory_mb=peak_memory,
            stage_results=stage_results,
            quality_gates=quality_gates,
            overall_result=overall_result
        )
        
        await self._repository.save_report(report)
        return report
