import pytest
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext
from backend.paper_fill_engine.core.stages import DeterministicFillStage
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.exceptions.exceptions import PaperFillSimulationError

@pytest.fixture
def stage():
    return DeterministicFillStage()

@pytest.mark.asyncio
async def test_zero_fill(stage, dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="AAPL", timeframe="1D", dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100, "simulated_fills": []},
        metadata=dummy_metadata
    )
    pipeline_context = PaperFillPipelineContext(execution_context=context)
    await stage.execute(context, pipeline_context)
    
    assert pipeline_context.simulation_result is not None
    assert pipeline_context.simulation_result.fill_state == FillState.PENDING_FILL
    assert pipeline_context.simulation_result.total_filled_quantity == 0
    assert pipeline_context.simulation_result.remaining_quantity == 100

@pytest.mark.asyncio
async def test_exact_fill(stage, dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="AAPL", timeframe="1D", dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100, "simulated_fills": [{"quantity": 100, "price": 150.0}]},
        metadata=dummy_metadata
    )
    pipeline_context = PaperFillPipelineContext(execution_context=context)
    await stage.execute(context, pipeline_context)
    
    res = pipeline_context.simulation_result
    assert res.fill_state == FillState.FILLED
    assert res.total_filled_quantity == 100
    assert res.remaining_quantity == 0
    assert res.average_fill_price == 150.0
    assert len(res.fill_events) == 1

@pytest.mark.asyncio
async def test_multiple_partial_fills(stage, dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="AAPL", timeframe="1D", dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100, "simulated_fills": [
            {"quantity": 30, "price": 100.0, "fill_id": "f1"},
            {"quantity": 40, "price": 110.0, "fill_id": "f2"},
            {"quantity": 30, "price": 120.0, "fill_id": "f3"}
        ]},
        metadata=dummy_metadata
    )
    pipeline_context = PaperFillPipelineContext(execution_context=context)
    await stage.execute(context, pipeline_context)
    
    res = pipeline_context.simulation_result
    assert res.fill_state == FillState.FILLED
    assert res.total_filled_quantity == 100
    assert res.remaining_quantity == 0
    # Avg price = (3000 + 4400 + 3600) / 100 = 110.0
    assert res.average_fill_price == 110.0
    assert len(res.fill_events) == 3
    assert res.fill_events[0].remaining_quantity_after_fill == 70
    assert res.fill_events[1].remaining_quantity_after_fill == 30
    assert res.fill_events[2].remaining_quantity_after_fill == 0

@pytest.mark.asyncio
async def test_overfill_protection(stage, dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="AAPL", timeframe="1D", dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100, "simulated_fills": [{"quantity": 120, "price": 150.0}]},
        metadata=dummy_metadata
    )
    pipeline_context = PaperFillPipelineContext(execution_context=context)
    
    with pytest.raises(PaperFillSimulationError):
        await stage.execute(context, pipeline_context)

@pytest.mark.asyncio
async def test_duplicate_fill_id(stage, dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="AAPL", timeframe="1D", dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100, "simulated_fills": [
            {"quantity": 50, "price": 150.0, "fill_id": "dup-id"},
            {"quantity": 50, "price": 150.0, "fill_id": "dup-id"}
        ]},
        metadata=dummy_metadata
    )
    pipeline_context = PaperFillPipelineContext(execution_context=context)
    
    with pytest.raises(PaperFillSimulationError):
        await stage.execute(context, pipeline_context)
