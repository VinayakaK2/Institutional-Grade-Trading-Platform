from typing import List
from backend.core.logger import get_logger
from backend.universe_engine.contracts.certification import ICertificationStage, IUniverseCertificationFacade
from backend.universe_engine.certification.models import UniverseCertificationContext
from backend.universe_engine.certification.exceptions import CertificationVerificationError

logger = get_logger(__name__)

class UniverseCertificationPipeline:
    """
    Executes a sequence of ICertificationStage instances.
    """
    
    def __init__(self, stages: List[ICertificationStage]):
        self._stages = stages
        
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> UniverseCertificationContext:
        """
        Executes all certification stages. Halts immediately if an unrecoverable
        CertificationVerificationError is raised by any stage.
        """
        logger.info(f"Starting Certification Pipeline execution for run {context.run_id}")
        
        pipeline_halted = False
        
        for stage in self._stages:
            stage_name = stage.__class__.__name__
            logger.info(f"Executing stage: {stage_name}")
            try:
                await stage.execute(context, facade)
            except CertificationVerificationError as e:
                logger.error(f"Pipeline halted at stage {stage_name} due to critical verification failure: {str(e)}")
                context.test_results[f"{stage_name}_halted"] = str(e)
                # Ensure context reflects overall failure
                context.is_certified = False
                pipeline_halted = True
                break
            except Exception as e:
                logger.error(f"Pipeline halted at stage {stage_name} due to unexpected error: {str(e)}")
                context.test_results[f"{stage_name}_error"] = str(e)
                context.is_certified = False
                pipeline_halted = True
                raise
                
        # Determine overall certification status only if we didn't halt
        if not pipeline_halted:
            context.is_certified = (
                context.functional_passed and 
                context.determinism_passed and 
                context.integrity_passed and 
                context.stress_passed
            )
        
        return context
