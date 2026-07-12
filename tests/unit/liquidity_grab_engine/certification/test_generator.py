import pytest
from backend.liquidity_grab_engine.certification.generator.generator import DeterministicDatasetGenerator

def test_generator_valid():
    ctx = DeterministicDatasetGenerator.generate_valid_liquidity_grab()
    assert ctx.dataset_version == 1
    assert ctx.candidate.symbol_id == "VALID_1"
    
def test_generator_failed():
    ctx = DeterministicDatasetGenerator.generate_failed_recovery(version=2)
    assert ctx.dataset_version == 2
    assert ctx.candidate.symbol_id == "FAILED_RECOVERY_2"
    
def test_generator_stress():
    ctxs = DeterministicDatasetGenerator.generate_stress_dataset(10, version=1)
    assert len(ctxs) == 10
    assert ctxs[0].candidate.symbol_id == "STRESS_1_0"
    assert ctxs[9].candidate.symbol_id == "STRESS_1_9"
