import logging
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport
from backend.liquidity_grab_engine.quality.pipeline.pipeline import LiquidityGrabQualityPipeline
from backend.liquidity_grab_engine.quality.contracts.repository import ILiquidityGrabQualityRepository
from backend.liquidity_grab_engine.quality.validation.structural import QualityStructuralValidator
from backend.liquidity_grab_engine.quality.validation.consistency import QualityConsistencyValidator

logger = logging.getLogger(__name__)

class LiquidityGrabQualityEngine:
    """
    Thin orchestrator for Phase 9.3 Quality Evaluation.
    """
    def __init__(self, pipeline: LiquidityGrabQualityPipeline, repository: ILiquidityGrabQualityRepository):
        self.pipeline = pipeline
        self.repository = repository
        self.structural_validator = QualityStructuralValidator()
        self.consistency_validator = QualityConsistencyValidator()
        
    async def evaluate(self, context: LiquidityGrabEvaluationContext) -> LiquidityGrabQualityReport:
        """
        Orchestrates evaluation and persists the report.
        """
        logger.info(f"Starting Quality Evaluation for candidate {context.candidate.candidate_id}.")
        
        if not self.structural_validator.validate(context):
            raise ValueError("Structural validation failed.")
            
        if not self.consistency_validator.validate(context):
            raise ValueError("Consistency validation failed.")
            
        report = self.pipeline.execute(context)
        
        await self.repository.save(report)
        logger.info(f"Report {report.report_id} persisted successfully.")
        
        return report
