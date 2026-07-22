import pytest
from backend.portfolio_state_engine.models.context import PortfolioStateExecutionContext, PortfolioStatePipelineContext
from backend.portfolio_state_engine.models.state import OpenPosition, CapitalSummary
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_state_engine.pipeline.snapshot_assembly import SnapshotAssemblyStage
from backend.portfolio_state_engine.pipeline.pipeline import PortfolioStatePipeline, PortfolioStatePipelineError
from backend.portfolio_state_engine.rules.structural_rules import PortfolioStateStructuralRules
from backend.portfolio_state_engine.rules.consistency_rules import PortfolioStateConsistencyRules
from backend.portfolio_state_engine.repository.memory_repo import MemoryPortfolioStateRepository
from backend.portfolio_state_engine.services.query_service import MemoryPortfolioStateQueryService
from backend.portfolio_state_engine.builders.snapshot_builder import PortfolioStateSnapshotBuilder

@pytest.fixture
def valid_context():
    return PortfolioStateExecutionContext(
        positions=[
            OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0)
        ],
        pending_orders=[],
        capital=CapitalSummary(available_capital=10000.0, used_capital=1500.0, cash_balance=11500.0),
        realized_pnl=50.0,
        unrealized_pnl=50.0,
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1.0"),
        dataset_version="v1.0",
        configuration=PortfolioConfiguration()
    )

def test_structural_rules(valid_context):
    rules = PortfolioStateStructuralRules()
    
    # Valid
    res = rules.validate(valid_context)
    assert res.is_valid
    
    # Invalid
    invalid = valid_context.model_copy(update={"dataset_version": ""})
    res = rules.validate(invalid)
    assert not res.is_valid
    assert "Dataset version is required" in res.reason

def test_consistency_rules(valid_context):
    rules = PortfolioStateConsistencyRules()
    
    # Valid
    res = rules.validate(valid_context)
    assert res.is_valid
    
    # Invalid dataset version format
    invalid = valid_context.model_copy(update={"dataset_version": "1.0"})
    res = rules.validate(invalid)
    assert not res.is_valid
    assert "must follow 'vX'" in res.reason
    
    # Negative capital
    invalid_cap = valid_context.model_copy(update={"capital": CapitalSummary(available_capital=-100.0, used_capital=0, cash_balance=0)})
    res = rules.validate(invalid_cap)
    assert not res.is_valid
    assert "cannot be negative" in res.reason

@pytest.mark.asyncio
async def test_snapshot_assembly_duplicate_checks(valid_context):
    stage = SnapshotAssemblyStage()
    
    # Duplicate positions
    dup_positions = [
        OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0),
        OpenPosition(symbol="AAPL", quantity=5, average_entry_price=152.0, current_price=155.0)
    ]
    invalid_ctx = valid_context.model_copy(update={"positions": dup_positions})
    
    pipeline_ctx = PortfolioStatePipelineContext(
        execution_context=invalid_ctx,
        execution_id="123"
    )
    # The positions are not in portfolio_state until PositionAssemblyStage, so we mock the intermediate state
    pipeline_ctx = pipeline_ctx.model_copy(
        update={"portfolio_state": pipeline_ctx.portfolio_state.model_copy(update={"positions": dup_positions})}
    )
    
    with pytest.raises(PortfolioStatePipelineError, match="Duplicate positions"):
        await stage.execute(pipeline_ctx)

@pytest.mark.asyncio
async def test_memory_repo_and_query_service():
    repo = MemoryPortfolioStateRepository()
    query_svc = MemoryPortfolioStateQueryService(repo)
    
    # Empty
    assert await query_svc.get_latest_state() is None
    assert await query_svc.get_history() == []
    
    # Missing snapshot load
    with pytest.raises(KeyError):
        await repo.load("nonexistent")
    
    assert await repo.exists("nonexistent") is False
    
def test_snapshot_builder_missing_fields():
    builder = PortfolioStateSnapshotBuilder()
    with pytest.raises(ValueError, match="required"):
        builder.build()

@pytest.mark.asyncio
async def test_pipeline_error_handling(valid_context):
    class FailingStage:
        async def execute(self, ctx):
            raise ValueError("Some random error")
            
    pipeline = PortfolioStatePipeline([FailingStage()])
    pipeline_ctx = PortfolioStatePipelineContext(
        execution_context=valid_context,
        execution_id="123"
    )
    
    with pytest.raises(PortfolioStatePipelineError, match="Pipeline execution failed: Some random error"):
        await pipeline.execute(pipeline_ctx)
