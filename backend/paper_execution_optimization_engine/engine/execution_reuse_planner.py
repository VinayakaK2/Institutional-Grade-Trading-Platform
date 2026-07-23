from typing import List, Tuple
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.engine.fingerprint_builder import OptimizationFingerprintBuilder

class ExecutionReusePlanner:
    """
    Identifies reusable execution snapshots and changed contexts.
    Performs dependency validation to instantly invalidate stale optimization configurations.
    """

    def __init__(
        self, 
        current_dataset_version: str,
        current_pipeline_version: str,
        current_optimization_config_hash: str
    ):
        self.current_dataset_version = current_dataset_version
        self.current_pipeline_version = current_pipeline_version
        self.current_optimization_config_hash = current_optimization_config_hash

    def plan_batch(
        self, 
        contexts: List[PaperExecutionOptimizationContext]
    ) -> List[Tuple[PaperExecutionOptimizationContext, str, bool]]:
        """
        Takes a batch of execution optimization contexts and returns a tuple for each containing:
        (Context, Generated Fingerprint, Is_Reusable)
        
        Is_Reusable is false if dependencies have shifted invalidating cache guarantees.
        """
        planned = []
        for ctx in contexts:
            # Dependency validation: Complete institutional check
            is_reusable = True
            
            if ctx.execution_context.dataset_version != self.current_dataset_version:
                is_reusable = False
            elif ctx.execution_context.metadata.get('pipeline_version') and ctx.execution_context.metadata.get('pipeline_version') != self.current_pipeline_version:
                is_reusable = False
            elif ctx.optimization_configuration.configuration_hash != self.current_optimization_config_hash:
                is_reusable = False
                
            fp = OptimizationFingerprintBuilder.build(ctx)
            planned.append((ctx, fp, is_reusable))
            
        return planned
