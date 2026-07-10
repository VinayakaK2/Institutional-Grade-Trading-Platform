import pytest

from backend.trend_engine.quality.pipeline.pipeline import TrendQualityPipeline
from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext

class MockStage(ITrendQualityStage):
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail
        
    async def execute(self, context: QualityExecutionContext) -> None:
        if self.should_fail:
            raise ValueError(f"Stage {self.name} failed.")
        context.metadata[self.name] = "Executed"


@pytest.mark.asyncio
async def test_pipeline_execution_order(context):
    stage1 = MockStage("Stage1")
    stage2 = MockStage("Stage2")
    
    pipeline = TrendQualityPipeline([stage1, stage2])
    await pipeline.execute(context)
    
    assert context.metadata["Stage1"] == "Executed"
    assert context.metadata["Stage2"] == "Executed"
    assert len(context.warnings) == 0

@pytest.mark.asyncio
async def test_pipeline_error_handling(context):
    stage1 = MockStage("Stage1", should_fail=True)
    stage2 = MockStage("Stage2")
    
    pipeline = TrendQualityPipeline([stage1, stage2])
    await pipeline.execute(context)
    
    # Even if stage1 fails, stage2 should execute, and warnings should be captured
    assert "Stage1" not in context.metadata
    assert context.metadata["Stage2"] == "Executed"
    assert len(context.warnings) == 1
    assert "failed" in context.warnings[0]
