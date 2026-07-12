import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration
from backend.liquidity_grab_engine.models.models import (
    LiquidityGrabPipelineVersion,
    LiquidityGrabConfigurationReference,
    LiquidityGrabMetadata,
    LiquidityGrabExecutionContext,
    LiquidityGrabSnapshot
)

def test_immutability():
    config = LiquidityGrabConfiguration()
    meta = LiquidityGrabMetadata(
        execution_start_timestamp=datetime.now(timezone.utc),
        pipeline_version="1.0"
    )
    context = LiquidityGrabExecutionContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.H1,
        dataset_version=1,
        parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1,
        configuration=config,
        metadata=meta
    )
    
    with pytest.raises(ValidationError):
        context.dataset_version = 2
        
def test_snapshot_id_generation():
    id1 = LiquidityGrabSnapshot.generate_id("AAPL:NASDAQ", "1h", 1, 1, 1)
    id2 = LiquidityGrabSnapshot.generate_id("AAPL:NASDAQ", "1h", 1, 1, 1)
    id3 = LiquidityGrabSnapshot.generate_id("AAPL:NASDAQ", "1h", 1, 1, 2)
    assert id1 == id2
    assert id1 != id3
