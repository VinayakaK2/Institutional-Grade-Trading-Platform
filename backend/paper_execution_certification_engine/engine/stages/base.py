from abc import ABC, abstractmethod
from typing import List
import time

from backend.paper_execution_certification_engine.models.snapshot import StageResult
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.exceptions.exceptions import CertificationFailedError

class ICertificationStage(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    async def execute(self, context: PaperExecutionCertificationContext, previous_results: List[StageResult]) -> StageResult:
        start_time = time.time()
        try:
            evidence = await self._run_verification(context, previous_results)
            duration = (time.time() - start_time) * 1000
            return StageResult(
                stage_name=self.name,
                passed=True,
                evidence=evidence,
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            if context.certification_configuration.fail_fast:
                raise CertificationFailedError(f"Stage {self.name} failed: {str(e)}") from e
            return StageResult(
                stage_name=self.name,
                passed=False,
                error_message=str(e),
                duration_ms=duration
            )
            
    @abstractmethod
    async def _run_verification(self, context: PaperExecutionCertificationContext, previous_results: List[StageResult]) -> dict:
        """Runs verification logic and returns an evidence dictionary on success, or raises Exception on failure."""
        pass
