"""
Unit tests for the Watchlist Certification Framework.
"""
import pytest
from typing import List

from backend.watchlist_engine.certification.mock_generator import MockDatasetGenerator
from backend.watchlist_engine.certification.pipeline import CertificationPipeline
from backend.watchlist_engine.certification.models import CertificationContext, CertificationStageResult
from backend.watchlist_engine.certification.contracts import ICertificationStage


def test_mock_generator_is_deterministic():
    gen1 = MockDatasetGenerator(seed=123)
    cands1 = gen1.generate_candidates("standard", 10)
    
    gen2 = MockDatasetGenerator(seed=123)
    cands2 = gen2.generate_candidates("standard", 10)
    
    assert len(cands1) == 10
    assert len(cands2) == 10
    
    # Check symbols are identical
    for c1, c2 in zip(cands1, cands2):
        assert c1.watchlist_symbol.symbol.symbol == c2.watchlist_symbol.symbol.symbol


def test_mock_generator_scenarios():
    gen = MockDatasetGenerator(seed=42)
    
    empty = gen.generate_candidates("empty_universe")
    assert len(empty) == 0
    
    manual = gen.generate_candidates("manual_include_only", 5)
    assert len(manual) == 5
    assert all(c.stage_metadata.get("manual_include") is True for c in manual)
    
    duplicates = gen.generate_candidates("duplicate_symbols", 20)
    assert len(duplicates) == 20
    # There should only be 10 unique symbols
    unique_symbols = set(c.watchlist_symbol.symbol.symbol for c in duplicates)
    assert len(unique_symbols) == 10
    
    single = gen.generate_candidates("single_symbol")
    assert len(single) == 1
    
    missing = gen.generate_candidates("missing_canonical_dataset", 5)
    assert len(missing) == 5
    
    excluded = gen.generate_candidates("all_symbols_excluded", 3)
    assert len(excluded) == 3


@pytest.mark.asyncio
async def test_certification_pipeline_aggregation():
    class DummyStage(ICertificationStage):
        @property
        def name(self) -> str:
            return "Dummy"
        async def execute(self, context: CertificationContext) -> CertificationStageResult:
            return CertificationStageResult(
                stage_name="Dummy", passed=True, execution_time_ms=5.0
            )
            
    pipeline = CertificationPipeline()
    pipeline.register_stage(DummyStage())
    
    context = CertificationContext()
    await pipeline.execute(context)
    
    assert len(context.stage_results) == 1
    assert context.stage_results[0].stage_name == "Dummy"

@pytest.mark.asyncio
async def test_certification_engine_end_to_end():
    from backend.watchlist_engine.certification.engine import CertificationEngine
    engine = CertificationEngine()
    report = await engine.run_certification()
    assert report.passed is True
