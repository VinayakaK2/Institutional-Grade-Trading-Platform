from typing import List, Any

from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration
from backend.liquidity_grab_engine.detection.contracts.market_data import ICandleSeries

from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate, CandidateVersion, CandidateMetadata, DetectionEvidence
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport, QualityEvidence, ClassificationSummary, EvaluationMetadata, LiquidityGrabQualityEnum
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext

class MockCandleSeries(ICandleSeries):
    def __init__(self, candles: List[Any]):
        self._candles = candles
        
    def get_candles(self) -> Any:
        return self._candles
        
    def __len__(self) -> int:
        return len(self._candles)

class DeterministicDatasetGenerator:
    """
    Generates deterministic datasets for certification testing.
    Outputs `LiquidityGrabLifecycleContext` expected by the OptimizationEngine.
    """
    
    @staticmethod
    def _create_base_context(
        symbol_code: str, 
        dataset_version: int, 
        candles: List[Any]
    ) -> LiquidityGrabLifecycleContext:
        
        cand_id = LiquidityGrabCandidate.generate_id(symbol_code, dataset_version, 1, 1, "h")
        
        candidate = LiquidityGrabCandidate(
            candidate_id=cand_id,
            symbol_id=symbol_code,
            timeframe="H1",
            dataset_version=dataset_version,
            parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1,
            configuration_hash="h",
            evidence=DetectionEvidence(),
            metadata=CandidateMetadata(pipeline_version="1.0.0", strategy_versions={}),
            version=CandidateVersion(version=1)
        )
        
        quality = LiquidityGrabQualityReport(
            report_id=f"qr_{cand_id}",
            candidate_id=cand_id,
            symbol_id=symbol_code,
            timeframe="H1",
            dataset_version=dataset_version,
            parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1,
            configuration_hash="h",
            evidence=QualityEvidence(),
            classification=ClassificationSummary(quality=LiquidityGrabQualityEnum.GOOD, classifier_algorithm_version="1.0", classifier_configuration_hash="h"),
            metadata=EvaluationMetadata(pipeline_version="1.0.0")
        )
        
        metadata = LiquidityGrabLifecycleContext.Metadata(pipeline_version="1.0.0")
        
        return LiquidityGrabLifecycleContext(
            candidate=candidate,
            quality_report=quality,
            evaluation_candles=MockCandleSeries(candles),
            dataset_version=dataset_version,
            configuration=LiquidityGrabConfiguration(),
            metadata=metadata
        )

    @staticmethod
    def generate_valid_liquidity_grab(version: int = 1) -> LiquidityGrabLifecycleContext:
        """Scenario: A valid liquidity grab (e.g. support break and recovery)."""
        return DeterministicDatasetGenerator._create_base_context(f"VALID_{version}", version, [])
        
    @staticmethod
    def generate_failed_recovery(version: int = 1) -> LiquidityGrabLifecycleContext:
        """Scenario: Failed recovery."""
        return DeterministicDatasetGenerator._create_base_context(f"FAILED_RECOVERY_{version}", version, [])
        
    @staticmethod
    def generate_false_break(version: int = 1) -> LiquidityGrabLifecycleContext:
        """Scenario: False break."""
        return DeterministicDatasetGenerator._create_base_context(f"FALSE_BREAK_{version}", version, [])
        
    @staticmethod
    def generate_empty_dataset(version: int = 1) -> LiquidityGrabLifecycleContext:
        """Scenario: Empty dataset."""
        return DeterministicDatasetGenerator._create_base_context(f"EMPTY_{version}", version, [])
        
    @staticmethod
    def generate_stress_dataset(count: int, version: int = 1) -> List[LiquidityGrabLifecycleContext]:
        """Generates a large list of deterministic contexts for stress testing."""
        return [
            DeterministicDatasetGenerator._create_base_context(f"STRESS_{version}_{i}", version, [])
            for i in range(count)
        ]
