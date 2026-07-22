import hashlib
import json
import uuid
from typing import Dict, Any
from backend.portfolio_state_engine.models.context import PortfolioStateExecutionContext, PortfolioStatePipelineContext
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_state_engine.rules.structural_rules import PortfolioStateStructuralRules
from backend.portfolio_state_engine.rules.consistency_rules import PortfolioStateConsistencyRules
from backend.portfolio_state_engine.pipeline.pipeline import PortfolioStatePipeline
from backend.portfolio_state_engine.builders.snapshot_builder import PortfolioStateSnapshotBuilder
from backend.portfolio_state_engine.contracts.repository import IPortfolioStateRepository
from backend.portfolio_state_engine.exceptions import PortfolioStateValidationError

class PortfolioStateEngine:
    """
    Stateless orchestrator for the portfolio state construction.
    """
    def __init__(
        self,
        repository: IPortfolioStateRepository,
        structural_rules: PortfolioStateStructuralRules,
        consistency_rules: PortfolioStateConsistencyRules,
        pipeline: PortfolioStatePipeline
    ):
        self._repository = repository
        self._structural_rules = structural_rules
        self._consistency_rules = consistency_rules
        self._pipeline = pipeline
        
    async def execute(self, execution_context: PortfolioStateExecutionContext) -> PortfolioStateSnapshot:
        # 1. Validation
        if execution_context.configuration.validation_enabled:
            struct_result = self._structural_rules.validate(execution_context)
            if not struct_result.is_valid:
                if execution_context.configuration.fail_fast:
                    raise PortfolioStateValidationError(f"Structural Validation Failed: {struct_result.reason}")
                    
            const_result = self._consistency_rules.validate(execution_context)
            if not const_result.is_valid:
                if execution_context.configuration.fail_fast:
                    raise PortfolioStateValidationError(f"Consistency Validation Failed: {const_result.reason}")
                    
        # 2. Pipeline Execution
        execution_id = str(uuid.uuid4())
        pipeline_context = PortfolioStatePipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )
        
        final_pipeline_context = await self._pipeline.execute(pipeline_context)
        
        # 3. Snapshot Building
        business_config: Dict[str, Any] = {}
        config_hash = hashlib.sha256(json.dumps(business_config, sort_keys=True).encode()).hexdigest()
        
        builder = PortfolioStateSnapshotBuilder()
        snapshot = builder \
            .with_portfolio_state(final_pipeline_context.portfolio_state) \
            .with_dataset_version(execution_context.dataset_version) \
            .with_parent_snapshot_references(execution_context.parent_snapshot_references) \
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
