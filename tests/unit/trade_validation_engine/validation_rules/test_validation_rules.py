import pytest

from backend.trade_validation_engine.validation_rules.config.config import ValidationRulesConfig
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, ValidationStatus
from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.signal_aggregation.models.evidence import TrendEvidence, ConsolidationEvidence, LiquidityGrabEvidence

from backend.trade_validation_engine.validation_rules.rules.evidence_validation import (
    TrendEvidenceRule,
    ConsolidationEvidenceRule,
    LiquidityGrabEvidenceRule
)
from backend.trade_validation_engine.validation_rules.rules.consistency_validation import (
    DatasetConsistencyRule,
    SnapshotLineageRule
)
from backend.trade_validation_engine.validation_rules.registry.registry import RuleRegistry
from backend.trade_validation_engine.validation_rules.pipeline.pipeline import ValidationPipeline
from backend.trade_validation_engine.validation_rules.di.container import ValidationRulesContainer

@pytest.fixture
def base_config():
    return ValidationRulesConfig(fail_fast=False, diagnostic_mode=True)

@pytest.fixture
def valid_context(base_config):
    return ValidationContext(
        symbol="BTC/USD",
        timeframe="1H",
        dataset_version=1,
        aggregated_trade_snapshot_version="test_agg_version",
        configuration=base_config
    )

@pytest.fixture
def valid_aggregated_evidence():
    return AggregatedTradeEvidence(
        symbol="BTC/USD",
        timeframe="1H",
        dataset_version=1,
        configuration_hash="dummy_hash",
        trend_evidence=TrendEvidence(
            snapshot_version=1,
            dataset_version=1,
            configuration_hash="dummy",
            algorithm_version="1.0",
            trend_state="UPTREND",
            trend_quality=0.9
        ),
        consolidation_evidence=ConsolidationEvidence(
            snapshot_version=1,
            dataset_version=1,
            configuration_hash="dummy",
            algorithm_version="1.0",
            consolidation_state="BREAKOUT",
            consolidation_quality=0.8
        ),
        liquidity_grab_evidence=LiquidityGrabEvidence(
            snapshot_version=1,
            dataset_version=1,
            configuration_hash="dummy",
            algorithm_version="1.0",
            liquidity_grab_state="CONFIRMED",
            liquidity_grab_quality=0.85
        )
    )

@pytest.mark.asyncio
async def test_trend_evidence_rule(valid_context, valid_aggregated_evidence):
    rule = TrendEvidenceRule()
    result = await rule.validate(valid_context, valid_aggregated_evidence)
    assert result.status == "PASS"

    # Test missing evidence
    invalid_evidence = valid_aggregated_evidence.model_copy(update={"trend_evidence": None})
    result2 = await rule.validate(valid_context, invalid_evidence)
    assert result2.status == "FAIL"

@pytest.mark.asyncio
async def test_consolidation_evidence_rule(valid_context, valid_aggregated_evidence):
    rule = ConsolidationEvidenceRule()
    result = await rule.validate(valid_context, valid_aggregated_evidence)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_liquidity_grab_evidence_rule(valid_context, valid_aggregated_evidence):
    rule = LiquidityGrabEvidenceRule()
    result = await rule.validate(valid_context, valid_aggregated_evidence)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_dataset_consistency_rule(valid_context, valid_aggregated_evidence):
    rule = DatasetConsistencyRule()
    result = await rule.validate(valid_context, valid_aggregated_evidence)
    assert result.status == "PASS"

    # Test mismatch
    invalid_context = valid_context.model_copy(update={"dataset_version": 2})
    result2 = await rule.validate(invalid_context, valid_aggregated_evidence)
    assert result2.status == "FAIL"

@pytest.mark.asyncio
async def test_snapshot_lineage_rule(valid_context, valid_aggregated_evidence):
    rule = SnapshotLineageRule()
    result = await rule.validate(valid_context, valid_aggregated_evidence)
    assert result.status == "PASS"

    invalid_context = valid_context.model_copy(update={"symbol": "ETH/USD"})
    result2 = await rule.validate(invalid_context, valid_aggregated_evidence)
    assert result2.status == "FAIL"

@pytest.mark.asyncio
async def test_rule_registry():
    registry = RuleRegistry()
    rule = TrendEvidenceRule()
    registry.register(rule)
    assert len(registry.get_ordered_rules()) == 1

@pytest.mark.asyncio
async def test_pipeline_execution(valid_context, valid_aggregated_evidence):
    registry = RuleRegistry()
    registry.register(TrendEvidenceRule())
    registry.register(ConsolidationEvidenceRule())
    
    pipeline = ValidationPipeline(registry)
    results = await pipeline.execute(valid_context, valid_aggregated_evidence)
    assert len(results) == 2
    assert all(r.status == "PASS" for r in results)

@pytest.mark.asyncio
async def test_engine_execution(valid_context, valid_aggregated_evidence):
    container = ValidationRulesContainer()
    container.register_default_rules()
    
    engine = container.engine()
    report = await engine.run(valid_context, valid_aggregated_evidence)
    
    assert report.status == ValidationStatus.PASS
    assert report.summary.total_rules_executed == 5
    assert report.summary.passed_rules == 5
    assert report.summary.failed_rules == 0

    repo = container.repository()
    assert await repo.exists(report.validation_id)
