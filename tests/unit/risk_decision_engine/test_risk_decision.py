import pytest
from typing import List, Optional

from backend.risk_decision_engine.config.config import RiskDecisionConfig
from backend.risk_decision_engine.models.context import RiskDecisionContext, ParentSnapshotReferences
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.risk_decision_engine.models.evidence import StageStatus, DecisionType
from backend.risk_decision_engine.contracts.repository import IRiskDecisionSnapshotRepository
from backend.risk_decision_engine.validation.structural import StructuralValidationLayer
from backend.risk_decision_engine.validation.consistency import ConsistencyValidationLayer
from backend.risk_decision_engine.core.engine import RiskDecisionEngine

from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot, PositionRiskMetadata
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import RiskEvaluationReport, ValidationResult as RiskValidationResult, AbsoluteRiskEvidence, PercentageRiskEvidence, PerUnitRiskEvidence

from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot, PositionSizingMetadata
from backend.position_sizing_engine.models.context import PositionSizingContext, ParentRiskSnapshotReference
from backend.position_sizing_engine.models.report import PositionSizingReport, ValidationResult as SizingValidationResult, CapitalAllocationEvidence, MaximumRiskEvidence, RawPositionSizeEvidence, RoundLotEvidence, RemainingCashEvidence

from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot, PortfolioRiskMetadata
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext, ParentSnapshotReferences as PortfolioParentSnapshotReferences
from backend.portfolio_risk_engine.models.report import PortfolioRiskReport, ValidationResult as PortfolioValidationResult
from backend.portfolio_risk_engine.models.evidence import (
    PortfolioExposureEvidence, PositionExposureEvidence, SectorExposureEvidence,
    CorrelationEvidence, DailyRiskEvidence, OpenRiskEvidence
)
from backend.portfolio_risk_engine.config.config import PortfolioRiskConfig

class MockRepository(IRiskDecisionSnapshotRepository):
    def __init__(self):
        self.snapshots = {}
        
    async def save(self, snapshot: RiskDecisionSnapshot) -> None:
        self.snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str) -> Optional[RiskDecisionSnapshot]:
        return self.snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self.snapshots
        
    async def query_by_symbol(self, symbol: str) -> List[RiskDecisionSnapshot]:
        return []
        
    async def query_by_timeframe(self, timeframe: str) -> List[RiskDecisionSnapshot]:
        return []
        
    async def query_by_decision(self, decision: DecisionType) -> List[RiskDecisionSnapshot]:
        return []
        
    async def query_by_parent_portfolio_snapshot(self, portfolio_snapshot_id: str) -> List[RiskDecisionSnapshot]:
        return []
        
    async def load_latest(self) -> Optional[RiskDecisionSnapshot]:
        return list(self.snapshots.values())[-1] if self.snapshots else None

@pytest.fixture
def base_snapshots():
    risk_snapshot = RiskEvaluationSnapshot(
        snapshot_id="risk_123",
        context=PositionRiskEvaluationContext(
            symbol="AAPL",
            timeframe="1D",
            entry_price=150.0,
            initial_stop_loss=140.0,
            trade_decision_snapshot_version="td_123",
            market_data_snapshot_id="md_123",
            configuration={},
            metadata={}
        ),
        report=RiskEvaluationReport(
            validation_status=RiskValidationResult(is_valid=True, errors=[]),
            absolute_risk_evidence=AbsoluteRiskEvidence(metric_id="1", source_snapshot_id="td_123", calculation_metadata={}, entry_price=150.0, stop_loss=140.0, risk_distance=10.0, absolute_risk=10.0, calculation_method="fixed"),
            percentage_risk_evidence=PercentageRiskEvidence(metric_id="2", source_snapshot_id="td_123", calculation_metadata={}, entry_price=150.0, stop_loss=140.0, risk_distance=10.0, percentage_risk=0.066, calculation_method="fixed"),
            per_unit_risk_evidence=PerUnitRiskEvidence(metric_id="3", source_snapshot_id="td_123", calculation_metadata={}, entry_price=150.0, stop_loss=140.0, risk_per_unit=10.0, calculation_method="fixed"),
            configuration_version="1",
            algorithm_version="1"
        ),
        metadata=PositionRiskMetadata(execution_duration_ms=10, additional_info={})
    )
    
    sizing_snapshot = PositionSizingSnapshot(
        snapshot_id="size_123",
        context=PositionSizingContext(
            parent_risk_snapshot=ParentRiskSnapshotReference(snapshot_id="risk_123", snapshot_version="1", dataset_version="1", configuration_hash="1"),
            risk_evaluation_snapshot=risk_snapshot,
            available_capital=100000.0,
            allocation_configuration={"allocation_percentage": 0.10},
            instrument_metadata={"asset_type": "equity", "sector": "Technology"},
            configuration={},
            metadata={}
        ),
        report=PositionSizingReport(
            validation_status=SizingValidationResult(is_valid=True),
            capital_allocation_evidence=CapitalAllocationEvidence(metric_id="1", source_snapshot_id="risk_123", calculation_metadata={}, available_capital=100000.0, allocation_percentage=0.10, allocated_capital=10000.0),
            maximum_risk_evidence=MaximumRiskEvidence(metric_id="2", source_snapshot_id="risk_123", calculation_metadata={}, allocated_capital=10000.0, max_risk_percentage=0.02, max_risk_amount=200.0),
            raw_position_size_evidence=RawPositionSizeEvidence(metric_id="3", source_snapshot_id="risk_123", calculation_metadata={}, max_risk_amount=200.0, risk_per_unit=10.0, raw_position_size=20.0),
            round_lot_evidence=RoundLotEvidence(metric_id="4", source_snapshot_id="risk_123", calculation_metadata={}, raw_position_size=20.0, rounded_position_size=20.0, rounding_policy="equity"),
            remaining_cash_evidence=RemainingCashEvidence(metric_id="5", source_snapshot_id="risk_123", calculation_metadata={}, allocated_capital=10000.0, position_cost=3000.0, remaining_cash=7000.0),
            configuration_version="1",
            algorithm_version="1"
        ),
        metadata=PositionSizingMetadata(execution_duration_ms=5)
    )
    
    portfolio_snapshot = PortfolioRiskSnapshot(
        snapshot_id="port_123",
        context=PortfolioRiskContext(
            parent_snapshots=PortfolioParentSnapshotReferences(
                risk_snapshot_id="risk_123", risk_snapshot_version="1", 
                sizing_snapshot_id="size_123", sizing_snapshot_version="1", 
                dataset_version="1", configuration_hash="1"
            ),
            risk_evaluation_snapshot=risk_snapshot,
            position_sizing_snapshot=sizing_snapshot,
            configuration=PortfolioRiskConfig(),
            metadata={}
        ),
        report=PortfolioRiskReport(
            validation_status=PortfolioValidationResult(is_valid=True),
            portfolio_exposure_evidence=PortfolioExposureEvidence(metric_id="1", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, current_portfolio_risk=0.0, new_position_risk=0.0, projected_portfolio_risk=0.0, max_portfolio_risk_limit=0.0),
            position_exposure_evidence=PositionExposureEvidence(metric_id="2", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, symbol="AAPL", current_position_exposure=0.0, new_position_exposure=0.0, projected_position_exposure=0.0, max_position_exposure_limit=0.0),
            sector_exposure_evidence=SectorExposureEvidence(metric_id="3", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, sector="Tech", current_sector_exposure=0.0, new_position_exposure=0.0, projected_sector_exposure=0.0, max_sector_exposure_limit=0.0),
            correlation_evidence=CorrelationEvidence(metric_id="4", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, symbol="AAPL", highly_correlated_assets={}, max_correlation_limit=0.0),
            daily_risk_evidence=DailyRiskEvidence(metric_id="5", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, current_daily_loss=0.0, new_position_risk=0.0, projected_daily_risk=0.0, max_daily_loss_limit=0.0),
            open_risk_evidence=OpenRiskEvidence(metric_id="6", source_snapshot_id="size_123", is_valid=True, calculation_metadata={}, current_open_risk=0.0, new_position_risk=0.0, projected_open_risk=0.0, max_open_risk_limit=0.0),
            configuration_version="1",
            algorithm_version="1"
        ),
        metadata=PortfolioRiskMetadata(execution_duration_ms=5, additional_info={})
    )
    
    return risk_snapshot, sizing_snapshot, portfolio_snapshot

@pytest.fixture
def valid_context(base_snapshots):
    risk_snapshot, sizing_snapshot, portfolio_snapshot = base_snapshots
    
    return RiskDecisionContext(
        parent_snapshots=ParentSnapshotReferences(
            risk_snapshot_id="risk_123",
            risk_snapshot_version="1.0.0",
            sizing_snapshot_id="size_123",
            sizing_snapshot_version="1.0.0",
            portfolio_snapshot_id="port_123",
            portfolio_snapshot_version="1.0.0",
            dataset_version="v1",
            configuration_hash="abc"
        ),
        risk_evaluation_snapshot=risk_snapshot,
        position_sizing_snapshot=sizing_snapshot,
        portfolio_risk_snapshot=portfolio_snapshot,
        configuration=RiskDecisionConfig()
    )

@pytest.mark.asyncio
async def test_structural_validation(valid_context):
    layer = StructuralValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid is True

@pytest.mark.asyncio
async def test_structural_validation_missing_fields(valid_context):
    layer = StructuralValidationLayer()
    invalid_context = valid_context.model_copy(update={"parent_snapshots": None})
    res = await layer.validate(invalid_context)
    assert res.is_valid is False
    assert "Parent snapshot references are required" in res.errors[0]

@pytest.mark.asyncio
async def test_consistency_validation(valid_context):
    layer = ConsistencyValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid is True

@pytest.mark.asyncio
async def test_consistency_validation_lineage_mismatch(valid_context):
    layer = ConsistencyValidationLayer()
    
    # Mismatch sizing_snapshot_id
    invalid_context = valid_context.model_copy(update={
        "parent_snapshots": valid_context.parent_snapshots.model_copy(update={"sizing_snapshot_id": "wrong_id"})
    })
    res = await layer.validate(invalid_context)
    assert res.is_valid is False
    assert "Position Sizing Snapshot ID does not match" in res.errors[0]

@pytest.mark.asyncio
async def test_engine_execution_success(valid_context):
    repo = MockRepository()
    engine = RiskDecisionEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        repository=repo
    )
    
    snapshot = await engine.evaluate(valid_context)
    
    assert snapshot is not None
    assert snapshot.report.final_decision_evidence.decision == DecisionType.APPROVED
    assert snapshot.report.validation_status.is_valid is True
    assert snapshot.report.risk_threshold_evidence.status == StageStatus.PASS
    assert snapshot.report.portfolio_constraint_evidence.status == StageStatus.PASS
    
    # Verify saved
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded is not None

@pytest.mark.asyncio
async def test_engine_execution_rejection(valid_context):
    repo = MockRepository()
    engine = RiskDecisionEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        repository=repo
    )
    
    # Force one of the portfolio evidence pieces to be invalid
    invalid_report = valid_context.portfolio_risk_snapshot.report.model_copy(update={
        "position_exposure_evidence": valid_context.portfolio_risk_snapshot.report.position_exposure_evidence.model_copy(update={"is_valid": False})
    })
    
    invalid_port_snapshot = valid_context.portfolio_risk_snapshot.model_copy(update={"report": invalid_report})
    
    reject_context = valid_context.model_copy(update={"portfolio_risk_snapshot": invalid_port_snapshot})
    
    snapshot = await engine.evaluate(reject_context)
    
    assert snapshot is not None
    assert snapshot.report.final_decision_evidence.decision == DecisionType.REJECTED
    assert snapshot.report.position_exposure_evidence.status == StageStatus.FAIL
    assert "PositionExposureStage" in snapshot.report.final_decision_evidence.triggered_rules
