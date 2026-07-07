import pytest
from backend.universe_engine.certification.mock_generator import DeterministicMockDatasetGenerator

def test_deterministic_generator_tiny():
    generator = DeterministicMockDatasetGenerator(seed=42)
    ds1 = generator.get_tiny_dataset()
    
    # Verify exact size
    assert len(ds1) == 10
    
    # Verify deterministic across instances with same seed
    gen2 = DeterministicMockDatasetGenerator(seed=42)
    ds2 = gen2.get_tiny_dataset()
    
    assert ds1 == ds2
    
def test_deterministic_generator_edge_cases():
    generator = DeterministicMockDatasetGenerator(seed=42)
    ds = generator.get_edge_case_dataset()
    
    assert len(ds) == 24
    
    # Check if duplicate is present
    symbols = [s.symbol for s in ds]
    assert symbols.count('TICK0') == 2
    
    missing_meta = [s for s in ds if s.symbol == 'SYM_MISSING'][0]
    # In the original SymbolReference model there is no metadata field.
    # So we can't assert on missing_meta.sector. Instead, we can just assert it exists.
    assert missing_meta is not None
