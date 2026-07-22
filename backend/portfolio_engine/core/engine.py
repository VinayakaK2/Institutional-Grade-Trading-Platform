import hashlib
import json
import uuid
from typing import Dict, Any
from backend.portfolio_engine.models.context import PortfolioExecutionContext, PortfolioPipelineContext
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot
from backend.portfolio_engine.validation.structural import StructuralValidator
from backend.portfolio_engine.validation.consistency import ConsistencyValidator
from backend.portfolio_engine.core.pipeline import PortfolioPipeline
from backend.portfolio_engine.builders.snapshot_builder import PortfolioSnapshotBuilder
from backend.portfolio_engine.contracts.repository import IPortfolioRepository
from backend.portfolio_engine.exceptions import PortfolioEngineError

class PortfolioEngine:
    """
    Stateless orchestrator for the portfolio lifecycle.
    """
    def __init__(
        self,
        repository: IPortfolioRepository,
        structural_validator: StructuralValidator,
        consistency_validator: ConsistencyValidator,
        pipeline: PortfolioPipeline
    ):
        self._repository = repository
        self._structural_validator = structural_validator
        self._consistency_validator = consistency_validator
        self._pipeline = pipeline
        
    async def execute(self, execution_context: PortfolioExecutionContext) -> PortfolioSnapshot:
        # 1. Validation
        if execution_context.configuration.validation_enabled:
            struct_result = self._structural_validator.validate(execution_context)
            if not struct_result.is_valid:
                # If fail_fast is enabled, we could throw here. We will throw an engine error as instructed.
                # Actually, the spec says "engine decides whether to throw", and fail-fast is config.
                if execution_context.configuration.fail_fast:
                    raise PortfolioEngineError(f"Structural Validation Failed: {struct_result.reason}")
                    
            const_result = self._consistency_validator.validate(execution_context)
            if not const_result.is_valid:
                if execution_context.configuration.fail_fast:
                    raise PortfolioEngineError(f"Consistency Validation Failed: {const_result.reason}")
                    
        # 2. Pipeline Execution
        execution_id = str(uuid.uuid4())
        pipeline_context = PortfolioPipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )
        
        await self._pipeline.execute(pipeline_context)
        
        # 3. Snapshot Building
        # Generate configuration hash (exclude infrastructure config like telemetry, debug, etc)
        # We assume for phase 12.1 there is no business config yet, so we hash a generic business namespace
        business_config: Dict[str, Any] = {} # e.g. sizing thresholds if we had them
        config_hash = hashlib.sha256(json.dumps(business_config, sort_keys=True).encode()).hexdigest()
        
        builder = PortfolioSnapshotBuilder()
        snapshot = builder \
            .with_dataset_version(execution_context.dataset_version) \
            .with_parent_snapshot_references(execution_context.parent_snapshot_references) \
            .with_configuration_hash(config_hash) \
            .with_pipeline_version(execution_context.configuration.pipeline_version) \
            .with_metadata({"execution_id": execution_id}) \
            .build()
            
        # 4. Persistence
        await self._repository.save(snapshot)
        
        return snapshot
