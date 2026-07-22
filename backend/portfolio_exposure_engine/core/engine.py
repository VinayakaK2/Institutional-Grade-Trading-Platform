import hashlib
import json
import uuid
from typing import Dict, Any
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposureExecutionContext, PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_exposure_engine.rules.structural_rules import PortfolioExposureStructuralRules
from backend.portfolio_exposure_engine.rules.consistency_rules import PortfolioExposureConsistencyRules
from backend.portfolio_exposure_engine.pipeline.pipeline import PortfolioExposurePipeline
from backend.portfolio_exposure_engine.builders.snapshot_builder import PortfolioExposureSnapshotBuilder
from backend.portfolio_exposure_engine.contracts.repository import IPortfolioExposureRepository
from backend.portfolio_exposure_engine.exceptions import PortfolioExposureValidationError

class PortfolioExposureEngine:
    """
    Stateless orchestrator for portfolio exposure calculations.
    """
    def __init__(
        self,
        repository: IPortfolioExposureRepository,
        structural_rules: PortfolioExposureStructuralRules,
        consistency_rules: PortfolioExposureConsistencyRules,
        pipeline: PortfolioExposurePipeline
    ):
        self._repository = repository
        self._structural_rules = structural_rules
        self._consistency_rules = consistency_rules
        self._pipeline = pipeline
        
    async def execute(self, execution_context: PortfolioExposureExecutionContext) -> PortfolioExposureSnapshot:
        # 1. Validation
        if execution_context.configuration.validation_enabled:
            struct_result = self._structural_rules.validate(execution_context)
            if not struct_result.is_valid:
                if execution_context.configuration.fail_fast:
                    raise PortfolioExposureValidationError(f"Structural Validation Failed: {struct_result.reason}")
                    
            const_result = self._consistency_rules.validate(execution_context)
            if not const_result.is_valid:
                if execution_context.configuration.fail_fast:
                    raise PortfolioExposureValidationError(f"Consistency Validation Failed: {const_result.reason}")
                    
        # 2. Pipeline Execution
        execution_id = str(uuid.uuid4())
        pipeline_context = PortfolioExposurePipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )
        
        final_pipeline_context = await self._pipeline.execute(pipeline_context)
        
        # 3. Snapshot Building
        business_config: Dict[str, Any] = {}
        config_hash = hashlib.sha256(json.dumps(business_config, sort_keys=True).encode()).hexdigest()
        
        builder = PortfolioExposureSnapshotBuilder()
        snapshot = builder \
            .with_exposure_analysis(final_pipeline_context.exposure_analysis) \
            .with_dataset_version(execution_context.portfolio_state_snapshot.dataset_version) \
            .with_parent_snapshot_references(execution_context.portfolio_state_snapshot.parent_snapshot_references) \
            .with_configuration_hash(config_hash) \
            .with_pipeline_version(execution_context.configuration.pipeline_version) \
            .with_metadata({
                "execution_id": execution_id,
                "stage_timings": final_pipeline_context.stage_timings
            }) \
            .build()
            
        # 4. Persistence
        await self._repository.save(snapshot)
        
        return snapshot
