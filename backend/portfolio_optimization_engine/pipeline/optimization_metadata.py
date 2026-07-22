from backend.portfolio_optimization_engine.contracts.pipeline import IPortfolioOptimizationStage
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationPipelineContext
from backend.portfolio_optimization_engine.models.optimization_models import OptimizationResult

class PortfolioOptimizationMetadataStage(IPortfolioOptimizationStage):
    """
    A non-algorithmic placeholder stage that strictly prepares deterministic 
    optimization metadata for execution phases without performing quantitative logic.
    """
    async def execute(self, context: PortfolioOptimizationPipelineContext) -> PortfolioOptimizationPipelineContext:
        
        # We simply construct the deterministic metadata from the configuration and aggregated facts
        metadata = {
            "aggregated_facts": context.aggregated_facts,
            "preparation_status": "READY_FOR_OPTIMIZATION"
        }
        
        context.optimization_result = OptimizationResult(
            metadata=metadata
        )
        
        return context
