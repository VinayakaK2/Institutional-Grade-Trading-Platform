import logging
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext

logger = logging.getLogger(__name__)

class LifecycleConsistencyValidator:
    def validate(self, context: LiquidityGrabLifecycleContext) -> None:
        logger.debug("Performing consistency validation on Lifecycle Context")
        
        candidate = context.candidate
        report = context.quality_report
        
        # 1. Candidate -> Quality Report matching
        if candidate.candidate_id != report.candidate_id:
            raise ValueError(
                f"Candidate ID mismatch. Candidate: {candidate.candidate_id}, "
                f"Quality Report: {report.candidate_id}"
            )
            
        # 2. Dataset version matching
        if context.dataset_version != candidate.dataset_version:
            raise ValueError(
                f"Dataset version mismatch. Context: {context.dataset_version}, "
                f"Candidate: {candidate.dataset_version}"
            )
            
        if context.dataset_version != report.dataset_version:
            raise ValueError(
                f"Dataset version mismatch. Context: {context.dataset_version}, "
                f"Quality Report: {report.dataset_version}"
            )
            
        # 3. Configuration compatibility
        context_config_hash = context.configuration.generate_hash()
        if context_config_hash != report.configuration_hash:
            raise ValueError(
                f"Configuration hash mismatch. Context config: {context_config_hash}, "
                f"Quality Report config: {report.configuration_hash}"
            )
