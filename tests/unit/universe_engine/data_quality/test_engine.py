import pytest
from datetime import datetime, timezone

from backend.universe_engine.data_quality.pipeline import DataQualityFilterPipeline
from backend.universe_engine.data_quality.engine import DataQualityFilterEngine
from backend.universe_engine.data_quality.models import DataQualityFilterConfiguration
from backend.universe_engine.data_quality.repository import (
    InMemoryDataQualityRepository,
)
from backend.universe_engine.data_quality.stages import (
    HistoricalDataAvailabilityFilter,
    MissingCandleDetection,
    SuspendedTradingDetection,
    DataCompletenessValidation,
    CorporateActionConsistency,
)
from backend.universe_engine.liquidity.models import (
    LiquidityQualifiedUniverse,
    LiquidityFilterConfiguration,
    LiquidityFilterStatistics,
)


@pytest.fixture
def test_pipeline():
    pipeline = DataQualityFilterPipeline()
    pipeline.register_stage(HistoricalDataAvailabilityFilter())
    pipeline.register_stage(MissingCandleDetection())
    pipeline.register_stage(SuspendedTradingDetection())
    pipeline.register_stage(DataCompletenessValidation())
    pipeline.register_stage(CorporateActionConsistency())
    return pipeline


@pytest.mark.asyncio
async def test_engine_full_pass(
    test_pipeline,
    mock_dq_data_provider,
    mock_calendar_provider,
    mock_corporate_action_provider,
    sample_instrument,
):
    repository = InMemoryDataQualityRepository()
    config = DataQualityFilterConfiguration(
        min_history_days=252,
        max_missing_candles_percentage=0.05,
        max_consecutive_suspensions=5,
        check_corporate_actions=True,
    )

    engine = DataQualityFilterEngine(
        config=config,
        pipeline=test_pipeline,
        data_provider=mock_dq_data_provider,
        calendar_provider=mock_calendar_provider,
        corporate_action_provider=mock_corporate_action_provider,
        repository=repository,
    )

    # Create fake parent universe
    parent_universe = LiquidityQualifiedUniverse(
        liquidity_universe_id="parent_uuid",
        parent_snapshot_id="snapshot_uuid",
        pipeline_version="1.0.0",
        config_hash="abc",
        created_at=datetime.now(timezone.utc),
        qualified_symbols=[sample_instrument],
        rejected_symbols=[],
        configuration_snapshot=LiquidityFilterConfiguration(),
        statistics=LiquidityFilterStatistics(),
    )

    result = await engine.generate_certified_universe("run_1", parent_universe)

    assert result.universe is not None
    assert result.universe.parent_snapshot_id == "parent_uuid"
    assert len(result.universe.certified_symbols) == 1
    assert result.universe.statistics.initial_instrument_count == 1
    assert result.universe.statistics.final_certified_count == 1

    loaded = await repository.load_certified_universe(
        result.universe.certified_universe_id
    )
    assert loaded is not None
    assert loaded.certified_symbols[0].symbol.symbol == "AAPL"

@pytest.mark.asyncio
async def test_engine_deterministic_behaviour(
    test_pipeline,
    mock_dq_data_provider,
    mock_calendar_provider,
    mock_corporate_action_provider,
    sample_instrument,
):
    """
    REGRESSION TEST: Verify that two identical executions using the same input dataset
    produce identical CertifiedUniverse outputs (excluding IDs and timestamps).
    """
    repository = InMemoryDataQualityRepository()
    config = DataQualityFilterConfiguration(
        min_history_days=252,
        max_missing_candles_percentage=0.05,
        max_consecutive_suspensions=5,
        check_corporate_actions=True,
    )

    engine = DataQualityFilterEngine(
        config=config,
        pipeline=test_pipeline,
        data_provider=mock_dq_data_provider,
        calendar_provider=mock_calendar_provider,
        corporate_action_provider=mock_corporate_action_provider,
        repository=repository,
    )

    parent_universe = LiquidityQualifiedUniverse(
        liquidity_universe_id="parent_uuid",
        parent_snapshot_id="snapshot_uuid",
        pipeline_version="1.0.0",
        config_hash="abc",
        created_at=datetime.now(timezone.utc),
        qualified_symbols=[sample_instrument],
        rejected_symbols=[],
        configuration_snapshot=LiquidityFilterConfiguration(),
        statistics=LiquidityFilterStatistics(),
    )

    result_1 = await engine.generate_certified_universe("run_1", parent_universe)
    result_2 = await engine.generate_certified_universe("run_2", parent_universe)

    u1 = result_1.universe
    u2 = result_2.universe

    # Core determinism checks
    assert u1.certified_symbols == u2.certified_symbols
    assert u1.rejected_symbols == u2.rejected_symbols
    assert u1.dataset_version == u2.dataset_version
    assert u1.config_hash == u2.config_hash
    assert u1.pipeline_version == u2.pipeline_version
    assert u1.statistics.initial_instrument_count == u2.statistics.initial_instrument_count
    assert u1.statistics.final_certified_count == u2.statistics.final_certified_count

