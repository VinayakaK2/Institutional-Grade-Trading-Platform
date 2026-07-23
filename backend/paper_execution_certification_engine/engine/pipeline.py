from typing import List
from backend.paper_execution_certification_engine.models.snapshot import StageResult
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.engine.stages.functional import FunctionalVerificationStage
from backend.paper_execution_certification_engine.engine.stages.determinism import DeterminismVerificationStage
from backend.paper_execution_certification_engine.engine.stages.repository import RepositoryVerificationStage
from backend.paper_execution_certification_engine.engine.stages.stress import StressVerificationStage
from backend.paper_execution_certification_engine.engine.stages.performance import PerformanceVerificationStage
from backend.paper_execution_certification_engine.engine.stages.regression import RegressionVerificationStage
from backend.paper_execution_certification_engine.engine.stages.coverage import CoverageVerificationStage
from backend.paper_execution_certification_engine.engine.stages.summary import CertificationSummaryStage

class PaperExecutionCertificationPipeline:
    """
    Sequential async execution pipeline. 
    Executes stages one by one. Does not execute stages in parallel.
    """
    
    def __init__(self):
        self._stages = [
            FunctionalVerificationStage(),
            DeterminismVerificationStage(),
            RepositoryVerificationStage(),
            StressVerificationStage(),
            PerformanceVerificationStage(),
            RegressionVerificationStage(),
            CoverageVerificationStage(),
            CertificationSummaryStage()
        ]
        
    async def execute(self, context: PaperExecutionCertificationContext) -> List[StageResult]:
        results: List[StageResult] = []
        for stage in self._stages:
            # We pass previous results to subsequent stages if they need them
            result = await stage.execute(context, results)
            results.append(result)
        return results
