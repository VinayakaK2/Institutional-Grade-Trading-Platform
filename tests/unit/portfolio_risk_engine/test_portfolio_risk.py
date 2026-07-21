import pytest
from typing import Dict, List, Optional
from backend.portfolio_risk_engine.config.config import PortfolioRiskConfig
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext, ParentSnapshotReferences
from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.contracts.repository import IPortfolioRiskSnapshotRepository
from backend.portfolio_risk_engine.validation.structural import StructuralValidationLayer
from backend.portfolio_risk_engine.validation.consistency import ConsistencyValidationLayer
from backend.portfolio_risk_engine.pipeline.pipeline import PortfolioRiskPipeline
from backend.portfolio_risk_engine.pipeline.stages.portfolio_exposure import MaximumPortfolioRiskStage
from backend.portfolio_risk_engine.pipeline.stages.position_exposure import PositionExposureStage
from backend.portfolio_risk_engine.pipeline.stages.sector_exposure import SectorExposureStage
from backend.portfolio_risk_engine.pipeline.stages.correlation_exposure import CorrelationExposureStage
from backend.portfolio_risk_engine.pipeline.stages.daily_risk import DailyRiskLimitStage
from backend.portfolio_risk_engine.pipeline.stages.open_risk import OpenRiskLimitStage
from backend.portfolio_risk_engine.core.engine import PortfolioRiskEngine
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot, PositionRiskMetadata
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import RiskEvaluationReport as RiskReport, ValidationResult as RiskValidationResult, AbsoluteRiskEvidence, PercentageRiskEvidence, PerUnitRiskEvidence
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot, PositionSizingMetadata
from backend.position_sizing_engine.models.context import PositionSizingContext, ParentRiskSnapshotReference
from backend.position_sizing_engine.models.report import PositionSizingReport, ValidationResult as SizingValidationResult, CapitalAllocationEvidence, MaximumRiskEvidence, RawPositionSizeEvidence, RoundLotEvidence, RemainingCashEvidence


class MockPortfolioSnapshotProvider(IPortfolioSnapshotProvider):
    def get_total_open_risk(self) -> float:
        return 1000.0
        
    def get_sector_exposure(self, sector: str) -> float:
        return 20000.0 if sector == "Technology" else 0.0
        
    def get_position_exposure(self, symbol: str) -> float:
        return 5000.0 if symbol == "AAPL" else 0.0
        
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        return {"AAPL": {"MSFT": 0.85, "GOOGL": 0.90, "TSLA": 0.3}}
        
    def get_daily_risk(self) -> float:
        return 500.0
        
    def get_open_positions_count(self) -> int:
        return 5

class MockRepository(IPortfolioRiskSnapshotRepository):
    def __init__(self):
        self.snapshots = {}
        
    async def save(self, snapshot: PortfolioRiskSnapshot) -> None:
        self.snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str) -> Optional[PortfolioRiskSnapshot]:
        return self.snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self.snapshots
        
    async def query_by_symbol(self, symbol: str) -> List[PortfolioRiskSnapshot]:
        return []
        
    async def query_by_timeframe(self, start_time: str, end_time: str) -> List[PortfolioRiskSnapshot]:
        return []
        
    async def query_by_parent_risk_snapshot(self, risk_snapshot_id: str) -> List[PortfolioRiskSnapshot]:
        return []
        
    async def query_by_parent_position_sizing_snapshot(self, sizing_snapshot_id: str) -> List[PortfolioRiskSnapshot]:
        return []
        
    async def load_latest(self) -> Optional[PortfolioRiskSnapshot]:
        return list(self.snapshots.values())[-1] if self.snapshots else None

@pytest.fixture
def base_snapshots():
    # Construct deep nested snapshot structure

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
        report=RiskReport(
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
    
    return risk_snapshot, sizing_snapshot

@pytest.fixture
def valid_context(base_snapshots):
    risk_snapshot, sizing_snapshot = base_snapshots
    
    return PortfolioRiskContext(
        parent_snapshots=ParentSnapshotReferences(
            risk_snapshot_id="risk_123",
            risk_snapshot_version="1.0.0",
            sizing_snapshot_id="size_123",
            sizing_snapshot_version="1.0.0",
            dataset_version="v1",
            configuration_hash="abc"
        ),
        risk_evaluation_snapshot=risk_snapshot,
        position_sizing_snapshot=sizing_snapshot,
        configuration=PortfolioRiskConfig()
    )

@pytest.mark.asyncio
async def test_structural_validation(valid_context):
    layer = StructuralValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid is True

@pytest.mark.asyncio
async def test_structural_validation_missing_snapshots(valid_context):
    layer = StructuralValidationLayer()
    
    # Missing parent_snapshots
    invalid_context = valid_context.model_copy(update={"parent_snapshots": None})
    res = await layer.validate(invalid_context)
    assert res.is_valid is False
    assert "Parent snapshot references are required." in res.errors[0]
    
    # Missing risk_evaluation_snapshot
    invalid_context_2 = valid_context.model_copy(update={"risk_evaluation_snapshot": None})
    res2 = await layer.validate(invalid_context_2)
    assert res2.is_valid is False
    assert "Risk Evaluation Snapshot is required." in res2.errors[0]
    
    # Missing position_sizing_snapshot
    invalid_context_3 = valid_context.model_copy(update={"position_sizing_snapshot": None})
    res3 = await layer.validate(invalid_context_3)
    assert res3.is_valid is False
    assert "Position Sizing Snapshot is required." in res3.errors[0]
    
    # Missing configuration
    invalid_context_4 = valid_context.model_copy(update={"configuration": None})
    res4 = await layer.validate(invalid_context_4)
    assert res4.is_valid is False
    assert "Configuration is strictly required." in res4.errors[0]

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
    assert "Position Sizing Snapshot ID does not match the Parent Reference ID." in res.errors[0]
    
    # Mismatch internal lineage (position sizing snapshot's parent risk snapshot != risk evaluation snapshot)
    invalid_risk_ref = valid_context.position_sizing_snapshot.context.parent_risk_snapshot.model_copy(update={"snapshot_id": "wrong_risk_id"})
    invalid_sizing_context = valid_context.position_sizing_snapshot.context.model_copy(update={"parent_risk_snapshot": invalid_risk_ref})
    invalid_sizing_snapshot = valid_context.position_sizing_snapshot.model_copy(update={"context": invalid_sizing_context})
    
    invalid_context_2 = valid_context.model_copy(update={"position_sizing_snapshot": invalid_sizing_snapshot})
    res2 = await layer.validate(invalid_context_2)
    assert res2.is_valid is False
    assert "Position Sizing Snapshot's parent risk snapshot does not match the provided Risk Evaluation Snapshot." in res2.errors[0]
    
    invalid_context = valid_context.model_copy(update={
        "parent_snapshots": ParentSnapshotReferences(
            risk_snapshot_id="risk_XXX",
            risk_snapshot_version="1",
            sizing_snapshot_id="size_123",
            sizing_snapshot_version="1",
            dataset_version="1",
            configuration_hash="1"
        )
    })
    res_bad = await layer.validate(invalid_context)
    assert res_bad.is_valid is False

@pytest.mark.asyncio
async def test_stages_and_pipeline(valid_context):
    provider = MockPortfolioSnapshotProvider()
    
    pipeline = PortfolioRiskPipeline([
        MaximumPortfolioRiskStage(),
        PositionExposureStage(),
        SectorExposureStage(),
        CorrelationExposureStage(),
        DailyRiskLimitStage(),
        OpenRiskLimitStage()
    ])
    
    evidence_bag = await pipeline.execute(valid_context, provider)
    
    # Assert specific Stage Values based on Mock Provider Outputs
    assert evidence_bag["portfolio_exposure"].projected_portfolio_risk == 1200.0 # 1000 + 200 (max risk)
    assert evidence_bag["position_exposure"].projected_position_exposure == 15000.0 # 5000 + 10000 (capital alloc)
    assert evidence_bag["sector_exposure"].projected_sector_exposure == 30000.0 # 20000 + 10000
    assert evidence_bag["correlation_exposure"].is_valid is True # only 2 highly correlated assets
    assert evidence_bag["daily_risk"].projected_daily_risk == 700.0 # 500 + 200
    assert evidence_bag["open_risk"].projected_open_risk == 6.0 # 5 + 1

@pytest.mark.asyncio
async def test_engine_execution_and_determinism(valid_context):
    provider = MockPortfolioSnapshotProvider()
    repo = MockRepository()
    
    engine = PortfolioRiskEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=PortfolioRiskPipeline([
            MaximumPortfolioRiskStage(),
            PositionExposureStage(),
            SectorExposureStage(),
            CorrelationExposureStage(),
            DailyRiskLimitStage(),
            OpenRiskLimitStage()
        ]),
        repository=repo
    )
    
    snapshot1 = await engine.execute(valid_context, provider)
    assert snapshot1.report.validation_status.is_valid is True
    assert snapshot1.snapshot_id is not None
    
    # Assert Determinism
    snapshot2 = await engine.execute(valid_context, provider)
    assert snapshot1.snapshot_id == snapshot2.snapshot_id
    assert snapshot1.created_at != snapshot2.created_at # Timestamps should differ
    
    # Asser persistence
    loaded = await repo.load(snapshot1.snapshot_id)
    assert loaded is not None
    assert loaded.snapshot_id == snapshot1.snapshot_id
