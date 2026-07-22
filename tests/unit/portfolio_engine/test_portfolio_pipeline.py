import pytest
from backend.portfolio_engine.core.pipeline import PortfolioPipeline
from backend.portfolio_engine.contracts.pipeline import IPortfolioPipelineStage
from backend.portfolio_engine.models.context import PortfolioPipelineContext, PortfolioExecutionContext
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_engine.exceptions import PortfolioPipelineError
import asyncio

class DummyStage(IPortfolioPipelineStage):
    async def execute(self, context: PortfolioPipelineContext) -> PortfolioPipelineContext:
        await asyncio.sleep(0.01)
        return context
        
class FailingStage(IPortfolioPipelineStage):
    async def execute(self, context: PortfolioPipelineContext) -> PortfolioPipelineContext:
        raise ValueError("Stage failed")

@pytest.fixture
def base_pipeline_context():
    exec_ctx = PortfolioExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1.0"),
        configuration=PortfolioConfiguration(pipeline_version="1.0")
    )
    return PortfolioPipelineContext(
        execution_context=exec_ctx,
        execution_id="123"
    )

@pytest.mark.asyncio
async def test_pipeline_execution(base_pipeline_context):
    pipeline = PortfolioPipeline(stages=[DummyStage()])
    result = await pipeline.execute(base_pipeline_context)
    
    assert "DummyStage" in result.stage_timings
    assert result.stage_timings["DummyStage"] > 0
    assert result.pipeline_metadata is not None
    assert result.pipeline_metadata.stage_count == 1
    
@pytest.mark.asyncio
async def test_pipeline_failure(base_pipeline_context):
    pipeline = PortfolioPipeline(stages=[FailingStage()])
    
    with pytest.raises(PortfolioPipelineError, match="Stage failed"):
        await pipeline.execute(base_pipeline_context)
