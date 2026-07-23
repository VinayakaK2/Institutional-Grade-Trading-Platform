from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext
from backend.paper_execution_optimization_engine.config.config import OptimizationConfig


class PaperExecutionOptimizationContext(BaseModel):
    """
    Context for paper execution optimization.
    Optimization happens before the result snapshot exists.
    """
    model_config = ConfigDict(frozen=True)

    execution_context: PaperExecutionResultExecutionContext = Field(
        description="The underlying paper execution context containing inputs for the result engine."
    )
    optimization_configuration: OptimizationConfig = Field(
        description="Configuration controlling optimization limits and caching behavior."
    )
    optimization_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the optimization process itself."
    )
