import pytest
from datetime import datetime, date
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.candle import Candle
from backend.market_data.models.timeframe import Timeframe
from backend.corporate_actions.models.action import CorporateAction, ActionType
from backend.corporate_actions.models.adjustment import AdjustmentMode
from backend.corporate_actions.infrastructure.storage import (
    InMemoryCorporateActionRepository, InMemoryDatasetVersionRepository, InMemoryAuditLogRepository
)
from backend.corporate_actions.validation.engine import ValidationEngine
from backend.corporate_actions.adjustment.engine import AdjustmentEngine
from backend.corporate_actions.pipeline.orchestrator import CorporateActionsPipeline, DatasetAdjustmentPipeline

@pytest.fixture
def sym():
    return SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))

@pytest.fixture
def base_dataset(sym):
    # Dataset from Jan 1 to Jan 5. 
    # Close prices: 100, 110, 120, 130, 140
    dataset = []
    for i in range(1, 6):
        dataset.append(Candle(
            symbol=sym,
            timeframe=Timeframe.D1,
            timestamp=datetime(2024, 1, i),
            open=100.0 + (i-1)*10,
            high=105.0 + (i-1)*10,
            low=95.0 + (i-1)*10,
            close=100.0 + (i-1)*10,
            volume=1000,
            is_completed=True
        ))
    return dataset

@pytest.fixture
def action_pipeline():
    return CorporateActionsPipeline(
        action_repo=InMemoryCorporateActionRepository(),
        audit_repo=InMemoryAuditLogRepository(),
        validation_engine=ValidationEngine()
    )

@pytest.fixture
def adjustment_pipeline(action_pipeline):
    return DatasetAdjustmentPipeline(
        action_repo=action_pipeline.action_repo,
        version_repo=InMemoryDatasetVersionRepository(),
        audit_repo=action_pipeline.audit_repo,
        adjustment_engine=AdjustmentEngine()
    )

def test_full_pipeline(sym, base_dataset, action_pipeline, adjustment_pipeline):
    # 1. Ingest Corporate Actions
    # A 2:1 Split on Jan 3
    split_action = CorporateAction(
        symbol=sym,
        action_type=ActionType.STOCK_SPLIT,
        effective_date=date(2024, 1, 3),
        ratio=2.0
    )
    
    # A $10 Cash Dividend on Jan 4
    # The close prior to Jan 4 is the Jan 3 close.
    # The Jan 3 close in the base dataset is 120.0.
    # BUT wait! We process chronologically backwards.
    # The Split on Jan 3 happens first in backward time (i.e. we adjust for dividend, then split? No, forward time: Split on Jan 3, Dividend on Jan 4).
    # Forward time: Split on Jan 3 means prices before Jan 3 are halved.
    # Dataset closes: [100, 110, 120, 130, 140]
    # Split on Jan 3 affects Jan 1 and Jan 2.
    # Dividend on Jan 4 affects Jan 1, Jan 2, and Jan 3.
    # Actually, the Dividend Adjustment needs the close price *prior* to Ex-Date as it exists *in the raw canonical dataset* or *the dataset after prior actions applied*?
    # Good question. If we iterate backwards in time, or process backwards.
    # Our engine applies actions using `prior_close` derived from the raw dataset loop in `_get_calculator()`.
    
    div_action = CorporateAction(
        symbol=sym,
        action_type=ActionType.CASH_DIVIDEND,
        effective_date=date(2024, 1, 4),
        amount=10.0
    )
    
    report = action_pipeline.process_actions([split_action, div_action])
    assert report.applied_actions == 2
    assert report.rejected_actions == 0
    
    # 2. Adjust Dataset
    adjusted_dataset, version = adjustment_pipeline.adjust_dataset(sym, base_dataset, AdjustmentMode.FULLY_ADJUSTED)
    
    assert len(adjusted_dataset) == 5
    
    # Jan 1 (Affected by Split and Div)
    # The close was 100.0. 
    # Dividend multiplier: prior close = 120.0 (from raw Jan 3). Multiplier = 1 - (10/120) = 0.91666...
    # Wait, the engine extracts prior close from the *raw* dataset passed in.
    # So for Jan 4 dividend, the prior close is Jan 3 (raw = 120.0). Multiplier = 1 - 10/120 = 110/120 = 0.916666
    # Let's check Jan 1 Close: 100 * (1/2) * (110/120) = 50 * 0.916666 = 45.83333
    jan_1_close = adjusted_dataset[0].close
    assert round(jan_1_close, 5) == round(100.0 * 0.5 * (110.0 / 120.0), 5)
    
    # Jan 3 (Affected by Div only, effective Jan 4)
    # The close was 120.0. 
    # Split was effective Jan 3, so Jan 3 is already split-adjusted in real life.
    # Therefore Split does NOT apply to Jan 3.
    # Dividend DOES apply to Jan 3.
    # Close = 120 * (110/120) = 110.0
    jan_3_close = adjusted_dataset[2].close
    assert round(jan_3_close, 5) == 110.0
    
    # Jan 5 (Unaffected by either)
    assert adjusted_dataset[4].close == 140.0
    
    # Check versioning
    assert version is not None
    assert version.original_version != version.adjusted_version
    assert len(version.applied_action_ids) == 2
