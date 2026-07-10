import pytest
from datetime import datetime, timezone

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.trend_engine.models.models import TrendSymbol, TrendDirection, TrendState, TrendSnapshot
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext

@pytest.fixture
def config():
    return TrendQualityConfig()

@pytest.fixture
def sample_trend_snapshot():
    sym = WatchlistSymbol(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        is_active=True,
        metadata={}
    )
    ts = TrendSymbol(
        watchlist_symbol=sym,
        direction=TrendDirection.UPTREND,
        state=TrendState.VALID,
        stage_metadata={}
    )
    return TrendSnapshot(
        snapshot_id="t_1",
        snapshot_version=1,
        source_watchlist_snapshot_id="w_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="i_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s_1",
        source_structure_snapshot_version=1,
        symbols=[ts],
        timestamp=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        pipeline_version="1.0.0",
        configuration_hash="hash",
        schema_version="1.0",
        fingerprint="fingerprint",
        execution_metadata={},
        audit_metadata={},
        metadata={}
    )

@pytest.fixture
def context(sample_trend_snapshot, config):
    return QualityExecutionContext(sample_trend_snapshot, config)
