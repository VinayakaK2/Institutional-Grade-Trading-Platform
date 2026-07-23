import pytest
from datetime import datetime, timezone
from backend.shared.snapshots.models import SnapshotReference
from backend.portfolio_decision_engine.models.decision_models import PortfolioDecision, DecisionStatus, DecisionMetadata
from backend.portfolio_decision_engine.models.references import PortfolioDecisionLineage
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot

from backend.paper_order_engine.models.order import OrderState
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot

from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.models.events import FillEvent
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot

from backend.paper_execution_quality_engine.models.execution_quality import (
    ExecutionQualityReport, SlippageMetrics, MarketImpactMetrics, SpreadMetrics,
    GapMetrics, LiquidityMetrics
)
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext

@pytest.fixture
def mock_decision_snapshot():
    metadata = DecisionMetadata(
        decision_id="dec_meta_1",
        pipeline_version="1.0",
        configuration_version="conf_1",
        engine_version="1.0",
        rule_version="1.0",
        execution_duration_ms=100,
        decision_timestamp=datetime.now(timezone.utc).isoformat()
    )
    decision = PortfolioDecision(
        status=DecisionStatus.APPROVED,
        reasons=[],
        metadata=metadata
    )
    lineage = PortfolioDecisionLineage(
        optimization_snapshot_id="opt_1",
        state_snapshot_id="state_1",
        risk_snapshot_id="risk_1",
        portfolio_state_snapshot=SnapshotReference(snapshot_id="ps_1"),
        portfolio_exposure_snapshot=SnapshotReference(snapshot_id="pe_1"),
        portfolio_correlation_snapshot=SnapshotReference(snapshot_id="pc_1"),
        risk_decision_snapshot=SnapshotReference(snapshot_id="rd_1"),
        candidate_position_snapshot=SnapshotReference(snapshot_id="cp_1")
    )
    return PortfolioDecisionSnapshot(
        snapshot_id="dec_1",
        schema_version="1.0",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc).isoformat(),
        decision=decision,
        lineage=lineage,
        configuration_snapshot_id="conf_1",
        business_fingerprint="finger_dec"
    )

@pytest.fixture
def mock_order_snapshot():
    return PaperOrderSnapshot(
        snapshot_id="ord_1",
        snapshot_version="ord_1",
        schema_version="1.0",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc).isoformat(),
        parent_portfolio_decision_snapshot_version="dec_1",
        parent_paper_execution_snapshot_version="none",
        order_state=OrderState.ACCEPTED,
        order_metadata={"quantity": 100, "symbol": "AAPL"},
        business_fingerprint="finger_ord",
        snapshot_hash="hash_ord"
    )

@pytest.fixture
def mock_fill_snapshot():
    event = FillEvent(
        fill_id="fill_1",
        quantity=100,
        price=150.0,
        timestamp=datetime.now(timezone.utc).isoformat(),
        sequence_number=1,
        remaining_quantity_after_fill=0
    )
    return PaperFillSnapshot(
        snapshot_id="fill_snap_1",
        snapshot_version="fill_snap_1",
        schema_version="1.0",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc).isoformat(),
        parent_paper_order_snapshot_version="ord_1",
        fill_state=FillState.FILLED,
        fill_events=[event],
        total_filled_quantity=100,
        remaining_quantity=0,
        average_fill_price=150.0,
        business_fingerprint="finger_fill",
        snapshot_hash="hash_fill"
    )

@pytest.fixture
def mock_eq_snapshot():
    report = ExecutionQualityReport(
        slippage=SlippageMetrics(expected_price=150.0, actual_fill_price=150.0, slippage_amount=0.0, slippage_percentage=0.0),
        market_impact=MarketImpactMetrics(expected_execution_price=150.0, market_impact=1.0, impact_percentage=1.0, impact_cost=2.0),
        spread_cost=SpreadMetrics(bid_price=149.9, ask_price=150.1, mid_price=150.0, effective_spread=0.2, paid_spread=10.0),
        gap_cost=GapMetrics(gap_up=False, gap_down=False, gap_size=0.0, gap_impact=0.0),
        liquidity_metrics=LiquidityMetrics(available_liquidity=1000.0, executed_quantity=100.0, remaining_liquidity=900.0, liquidity_utilization=0.1)
    )
    return PaperExecutionQualitySnapshot(
        snapshot_id="eq_1",
        snapshot_version="eq_1",
        schema_version="1.0",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc).isoformat(),
        parent_fill_snapshot_version="fill_snap_1",
        execution_quality_report=report,
        business_fingerprint="finger_eq",
        snapshot_hash="hash_eq"
    )

@pytest.fixture
def mock_execution_context(mock_decision_snapshot, mock_order_snapshot, mock_fill_snapshot, mock_eq_snapshot):
    return PaperExecutionResultExecutionContext(
        dataset_version="v1",
        configuration_hash="conf_hash",
        portfolio_decision_snapshot=mock_decision_snapshot,
        paper_order_snapshot=mock_order_snapshot,
        paper_fill_snapshot=mock_fill_snapshot,
        paper_execution_quality_snapshot=mock_eq_snapshot,
        metadata={"symbol": "AAPL", "requested_quantity": 100}
    )
