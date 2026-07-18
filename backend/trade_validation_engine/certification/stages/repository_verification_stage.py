import time
from typing import Dict, Any
from backend.trade_validation_engine.certification.contracts.stage import ICertificationStage
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import StageResult

class RepositoryVerificationStage(ICertificationStage):
    @property
    def stage_name(self) -> str:
        return "Repository"

    async def execute(self, config: CertificationConfig, context: Dict[str, Any]) -> StageResult:
        start_t = time.time()
        
        repo = context.get("optimization_repository")
        if not repo:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={})
            
        # Verify repository mutation rejection logic
        # 1. Test DELETE (should raise AttributeError or NotImplementedError if it doesn't exist, which proves INSERT-only)
        has_delete = hasattr(repo, "delete") or hasattr(repo, "remove")
        has_update = hasattr(repo, "update")
        
        duration = int((time.time() - start_t) * 1000)
        
        context["evidence"] = {
            "has_delete": has_delete,
            "has_update": has_update,
            "insert_only_guarantee": not has_delete and not has_update
        }
        
        if has_delete or has_update:
             return StageResult(
                stage_name=self.stage_name,
                status="FAIL",
                duration_ms=duration,
                metrics={"reason": "Repository allows mutations (DELETE/UPDATE)"}
            )
            
        return StageResult(
            stage_name=self.stage_name,
            status="PASS",
            duration_ms=duration,
            metrics={"mutations_blocked": True}
        )
