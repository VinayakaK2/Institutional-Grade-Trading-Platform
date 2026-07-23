from typing import List
from backend.paper_execution_certification_engine.engine.stages.base import ICertificationStage
from backend.paper_execution_certification_engine.models.snapshot import StageResult
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext

class CertificationSummaryStage(ICertificationStage):
    """
    Final stage in the sequential pipeline. 
    Verifies that all preceding stages completed successfully before 
    handing off to the Report Builder.
    """
    
    @property
    def name(self) -> str:
        return "Certification Summary"
        
    async def _run_verification(self, context: PaperExecutionCertificationContext, previous_results: List[StageResult]) -> dict:
        
        # Verify all previous stages passed
        all_passed = all(stage.passed for stage in previous_results)
        
        return {
            "all_previous_passed": all_passed,
            "stages_verified": len(previous_results)
        }
