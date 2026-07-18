import pytest
from backend.trade_validation_engine.trade_decision.di.container import TradeDecisionContainer
from backend.trade_validation_engine.trade_decision.models.models import DecisionState
from backend.trade_validation_engine.trade_decision.config.config import TradeDecisionConfig
from tests.unit.trade_validation_engine.trade_decision.conftest import MockValidStage, MockInvalidStage

@pytest.mark.asyncio
async def test_engine_determinism_regression(valid_context, mock_validation_report):
    container = TradeDecisionContainer()
    container.pipeline.register_stage(MockValidStage())
    engine = container.engine()
    
    # Run 100 times to prove determinism
    first_snapshot = await engine.execute(valid_context, mock_validation_report)
    assert first_snapshot.decision_state == DecisionState.VALID
    
    for _ in range(99):
        snapshot = await engine.execute(valid_context, mock_validation_report)
        assert snapshot.decision_id == first_snapshot.decision_id
        assert snapshot.decision_state == first_snapshot.decision_state
        assert snapshot.rejection_reasons == first_snapshot.rejection_reasons

@pytest.mark.asyncio
async def test_engine_resolver_override(valid_context, mock_validation_report):
    container = TradeDecisionContainer()
    container.pipeline.register_stage(MockValidStage())
    # Note: If fail_fast is on, the pipeline stops at Invalid. 
    context_no_fail_fast = valid_context.model_copy(
        update={"configuration": TradeDecisionConfig(fail_fast=False)}
    )
    container.pipeline.register_stage(MockInvalidStage())
    
    engine = container.engine()
    snapshot = await engine.execute(context_no_fail_fast, mock_validation_report)
    assert snapshot.decision_state == DecisionState.INVALID
    assert len(snapshot.rejection_reasons) == 1

@pytest.mark.asyncio
async def test_engine_builder_purity_and_fingerprint(valid_context, mock_validation_report):
    from backend.trade_validation_engine.trade_decision.engine.builder import TradeDecisionBuilder
    
    # Capture original state
    original_context_dict = valid_context.model_dump()
    
    snapshot1 = TradeDecisionBuilder.build(
        context=valid_context,
        final_state=DecisionState.VALID,
        rejection_reasons=[],
        stage_results=[]
    )
    
    # Prove builder purity
    assert valid_context.model_dump() == original_context_dict
    
    # Prove fingerprint identity
    snapshot2 = TradeDecisionBuilder.build(
        context=valid_context,
        final_state=DecisionState.VALID,
        rejection_reasons=[],
        stage_results=[]
    )
    assert snapshot1.business_fingerprint == snapshot2.business_fingerprint
    assert snapshot1.decision_id == snapshot2.decision_id

@pytest.mark.asyncio
async def test_engine_algorithm_version_id_difference(valid_context, mock_validation_report, monkeypatch):
    import backend.trade_validation_engine.trade_decision.engine.builder as builder
    
    monkeypatch.setattr(builder, "TRADE_DECISION_ALGORITHM_VERSION", "1.0.0")
    snapshot1 = builder.TradeDecisionBuilder.build(
        context=valid_context,
        final_state=DecisionState.VALID,
        rejection_reasons=[],
        stage_results=[]
    )
    
    monkeypatch.setattr(builder, "TRADE_DECISION_ALGORITHM_VERSION", "2.0.0")
    snapshot2 = builder.TradeDecisionBuilder.build(
        context=valid_context,
        final_state=DecisionState.VALID,
        rejection_reasons=[],
        stage_results=[]
    )
    
    assert snapshot1.decision_id != snapshot2.decision_id
    # Fingerprint purely business logic, unaffected by engine algorithm version
    assert snapshot1.business_fingerprint == snapshot2.business_fingerprint

